"""Celery worker for document translation."""

import json
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

from workers.celery_app import celery_app


@celery_app.task(bind=True, name="process_document", queue="translate")
def process_document(self, job_id: str):
    """
    Process a document translation job.
    
    1. Extract text blocks from document
    2. Detect language for each block
    3. Skip English, translate foreign languages
    4. Output as JSON or CSV
    """
    import asyncio
    asyncio.run(_process_document_async(job_id))


async def _process_document_async(job_id: str):
    """Async document processing."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    from config import settings
    from models.document import DocumentJob, DocumentStatus
    from services.extractors import get_extractor
    
    # Create async engine
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get job
        result = await session.execute(
            select(DocumentJob).where(DocumentJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return {"error": "Job not found"}
        
        try:
            start_time = time.time()
            
            # Update status
            job.status = DocumentStatus.EXTRACTING
            job.started_at = datetime.utcnow()
            await session.commit()
            
            # Extract text blocks
            extractor = get_extractor(job.file_type)
            blocks = list(extractor.extract(job.file_path))
            job.total_blocks = len(blocks)
            await session.commit()
            
            # Detect languages
            job.status = DocumentStatus.DETECTING
            await session.commit()
            
            from langdetect import detect
            from nllb_lang_codes import get_nllb_code
            
            lang_counts: Dict[str, int] = defaultdict(int)
            blocks_by_lang: Dict[str, List] = defaultdict(list)
            
            for block in blocks:
                try:
                    iso_code = detect(block.text)
                    lang_counts[iso_code] += 1
                    
                    if iso_code == "en":
                        # English - skip translation
                        block.translated = None
                        block.lang = "en"
                    else:
                        # Foreign - needs translation
                        nllb_code = get_nllb_code(iso_code)
                        block.lang = iso_code
                        block.nllb_code = nllb_code or "eng_Latn"
                        blocks_by_lang[iso_code].append(block)
                except Exception:
                    # Can't detect - assume English
                    block.translated = None
                    block.lang = "unknown"
            
            job.languages_found = dict(lang_counts)
            job.blocks_skipped = lang_counts.get("en", 0)
            await session.commit()
            
            # Translate foreign blocks
            job.status = DocumentStatus.TRANSLATING
            await session.commit()
            
            translated_count = 0
            for lang, lang_blocks in blocks_by_lang.items():
                # Batch translate blocks of same language
                for block in lang_blocks:
                    try:
                        translation = await translate_text(
                            block.text,
                            block.nllb_code,
                            job.target_lang,
                        )
                        block.translated = translation
                        translated_count += 1
                        
                        # Update progress
                        job.processed_blocks = job.blocks_skipped + translated_count
                        job.progress = int((job.processed_blocks / job.total_blocks) * 100)
                        await session.commit()
                    except Exception as e:
                        block.translated = f"[Translation error: {str(e)}]"
            
            job.blocks_translated = translated_count
            
            # Generate output
            output = generate_output(blocks, job.output_format)
            
            # Save output file
            output_dir = settings.upload_dir / "documents" / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{job.id}.{job.output_format}"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            
            job.output_path = str(output_path)
            job.status = DocumentStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.processing_time_ms = int((time.time() - start_time) * 1000)
            job.progress = 100
            await session.commit()
            
            # Log audit event
            await log_audit_event(
                session, job_id, "document_completed",
                job.processing_time_ms, "success", None,
                {
                    "total_blocks": job.total_blocks,
                    "blocks_translated": job.blocks_translated,
                    "blocks_skipped": job.blocks_skipped,
                    "languages_found": job.languages_found,
                }
            )
            
        except Exception as e:
            job.status = DocumentStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            await session.commit()
            
            await log_audit_event(
                session, job_id, "document_failed",
                None, "failed", str(e), None
            )
            raise


async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using NLLB model."""
    import ctranslate2
    import transformers
    from config import settings
    
    # Get model path
    model_path = settings.model_dir / "nllb-ct2" / "JustFrederik_nllb-200-distilled-600M-ct2-float16"
    if not model_path.exists():
        raise ValueError("No model available")
    
    # Load model (cached)
    tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    translator = ctranslate2.Translator(
        str(model_path),
        device=settings.device,
        compute_type=settings.compute_type,
    )
    
    # Tokenize
    tokenizer.src_lang = source_lang
    tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(text))
    
    # Translate
    results = translator.translate_batch(
        [tokens],
        target_prefix=[[target_lang]],
        beam_size=5,
    )
    
    # Decode
    target_tokens = results[0].hypotheses[0][1:]
    translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target_tokens))
    
    return translation


def generate_output(blocks, output_format: str) -> str:
    """Generate output in requested format."""
    if output_format == "json":
        output = []
        for block in blocks:
            item = {
                "text": block.text,
                "lang": getattr(block, "lang", "unknown"),
                "translated": getattr(block, "translated", None),
            }
            if block.page is not None:
                item["page"] = block.page
            output.append(item)
        return json.dumps(output, ensure_ascii=False, indent=2)
    
    elif output_format == "csv":
        import csv
        import io
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Page", "Original", "Language", "Translated"])
        
        for block in blocks:
            writer.writerow([
                block.page or "",
                block.text,
                getattr(block, "lang", "unknown"),
                getattr(block, "translated", "") or "",
            ])
        
        return buffer.getvalue()
    
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


async def log_audit_event(session, job_id, action, processing_time_ms, status, error_message, metadata):
    """Log audit event for document processing."""
    try:
        import sys
        sys.path.insert(0, "/app")
        from shared.models.audit import AuditLog
        from uuid import UUID
        
        audit = AuditLog(
            service="translate",
            action=action,
            job_id=UUID(job_id) if job_id else None,
            processing_time_ms=processing_time_ms,
            status=status,
            error_message=error_message,
            metadata=metadata,
        )
        session.add(audit)
        await session.commit()
    except Exception:
        pass
