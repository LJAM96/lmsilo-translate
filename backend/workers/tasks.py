"""Celery tasks for Translate."""

import time
from datetime import datetime

from workers.celery_app import celery_app


@celery_app.task(bind=True, name="translate_text")
def translate_text_task(self, job_id: str):
    """
    Process a translation job.
    
    Loads model, performs translation, updates job record.
    """
    import asyncio
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    from config import settings
    from models.job import TranslationJob
    from models.database import Model
    
    # Create async engine for this task
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def process():
        async with async_session() as session:
            # Get job
            result = await session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                return {"error": "Job not found"}
            
            try:
                # Update status
                job.status = "processing"
                job.started_at = datetime.utcnow()
                await session.commit()
                
                start_time = time.time()
                
                # Get model
                model_path = None
                if job.model_id:
                    result = await session.execute(
                        select(Model).where(Model.id == job.model_id)
                    )
                    model = result.scalar_one_or_none()
                    if model and model.local_path:
                        model_path = model.local_path
                        job.model_name = model.name
                
                # Perform translation
                translation, detected_lang = await perform_translation(
                    text=job.text,
                    source_lang=job.source_lang,
                    target_lang=job.target_lang,
                    model_path=model_path,
                )
                
                # Update job with results
                job.translation = translation
                job.detected_lang = detected_lang
                job.status = "completed"
                job.completed_at = datetime.utcnow()
                job.processing_time_ms = int((time.time() - start_time) * 1000)
                await session.commit()
                
                # Log audit event for completion
                await log_audit_event(
                    session, job_id, "job_completed", job.model_name,
                    job.processing_time_ms, "success", None,
                    {"translation_length": len(translation)}
                )
                
                return {"status": "completed", "job_id": job_id}
                
            except Exception as e:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                await session.commit()
                
                # Log audit event for failure
                await log_audit_event(
                    session, job_id, "job_failed", job.model_name,
                    None, "failed", str(e), None
                )
                raise
    
    return asyncio.run(process())


async def perform_translation(
    text: str,
    source_lang: str | None,
    target_lang: str,
    model_path: str | None = None,
) -> tuple[str, str | None]:
    """
    Perform actual translation using NLLB model.
    
    Returns (translation, detected_language)
    """
    import ctranslate2
    import transformers
    from config import settings
    
    # Use default model path if not specified
    if not model_path:
        default_model = settings.model_dir / "nllb-ct2" / "JustFrederik_nllb-200-distilled-600M-ct2-float16"
        if default_model.exists():
            model_path = str(default_model)
        else:
            raise ValueError("No model available. Please download a model first.")
    
    # Load tokenizer and translator
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        "facebook/nllb-200-distilled-600M"
    )
    translator = ctranslate2.Translator(
        model_path,
        device=settings.device,
        compute_type=settings.compute_type,
    )
    
    # Handle source language
    detected_lang = None
    if not source_lang:
        # Simple auto-detection fallback
        source_lang = "eng_Latn"
        detected_lang = source_lang
    
    # Tokenize
    tokenizer.src_lang = source_lang
    tokens = tokenizer.convert_ids_to_tokens(
        tokenizer.encode(text)
    )
    
    # Translate
    target_prefix = [target_lang]
    results = translator.translate_batch(
        [tokens],
        target_prefix=[target_prefix],
        beam_size=5,
    )
    
    # Decode
    target_tokens = results[0].hypotheses[0][1:]  # Skip language token
    translation = tokenizer.decode(
        tokenizer.convert_tokens_to_ids(target_tokens)
    )
    
    return translation, detected_lang


async def log_audit_event(
    session,
    job_id: str,
    action: str,
    model_used: str | None,
    processing_time_ms: int | None,
    status: str,
    error_message: str | None,
    metadata: dict | None,
):
    """Log an audit event from the Celery worker."""
    try:
        import sys
        sys.path.insert(0, "/app")
        from shared.models.audit import AuditLog
        from uuid import UUID
        
        audit = AuditLog(
            service="translate",
            action=action,
            job_id=UUID(job_id) if job_id else None,
            model_used=model_used,
            processing_time_ms=processing_time_ms,
            status=status,
            error_message=error_message,
            metadata=metadata,
        )
        session.add(audit)
        await session.commit()
    except ImportError:
        pass  # Shared module not available
    except Exception:
        pass  # Don't fail job on audit logging error
