"""Celery worker for document translation - OPTIMIZED VERSION."""

import json
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# ============= GLOBAL MODEL CACHE =============
# Models are loaded once per worker process and reused
_translator_cache: Dict[str, any] = {}
_tokenizer_cache: Dict[str, any] = {}


def get_cached_translator():
    """Get or create cached translator instance."""
    if "translator" not in _translator_cache:
        import ctranslate2
        from config import settings
        
        model_path = settings.model_dir / "nllb-ct2" / "JustFrederik_nllb-200-distilled-600M-ct2-float16"
        if not model_path.exists():
            raise ValueError("No model available")
        
        logger.info(f"Loading translator model (device={settings.device})...")
        _translator_cache["translator"] = ctranslate2.Translator(
            str(model_path),
            device=settings.device,
            compute_type=settings.compute_type,
            inter_threads=4,  # Parallel threads
            intra_threads=4,
        )
        logger.info("Translator model loaded and cached")
    
    return _translator_cache["translator"]


def get_cached_tokenizer():
    """Get or create cached tokenizer instance."""
    if "tokenizer" not in _tokenizer_cache:
        import transformers
        logger.info("Loading tokenizer...")
        _tokenizer_cache["tokenizer"] = transformers.AutoTokenizer.from_pretrained(
            "facebook/nllb-200-distilled-600M"
        )
        logger.info("Tokenizer loaded and cached")
    
    return _tokenizer_cache["tokenizer"]


# ============= BATCH SIZE CONFIG =============
BATCH_SIZE = 32  # Translate 32 texts at once
DETECTION_BATCH_SIZE = 100  # Detect language for 100 blocks at once
PROGRESS_UPDATE_INTERVAL = 50  # Update DB every 50 blocks


@celery_app.task(bind=True, name="process_document", queue="translate")
def process_document(self, job_id: str):
    """Process a document translation job with optimizations."""
    import asyncio
    asyncio.run(_process_document_async(job_id))


async def _process_document_async(job_id: str):
    """Async document processing with batch optimizations."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    from config import settings
    from models.document import DocumentJob, DocumentStatus
    from services.extractors import get_extractor
    
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(DocumentJob).where(DocumentJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return {"error": "Job not found"}
        
        try:
            start_time = time.time()
            
            # ===== STAGE 1: EXTRACTION =====
            job.status = DocumentStatus.EXTRACTING
            job.started_at = datetime.utcnow()
            await session.commit()
            
            extractor = get_extractor(job.file_type)
            blocks = list(extractor.extract(job.file_path))
            job.total_blocks = len(blocks)
            await session.commit()
            
            logger.info(f"Extracted {len(blocks)} blocks from {job.original_filename}")
            
            # ===== STAGE 2: PARALLEL LANGUAGE DETECTION =====
            job.status = DocumentStatus.DETECTING
            await session.commit()
            
            blocks, lang_counts, blocks_by_lang = detect_languages_parallel(blocks)
            
            job.languages_found = dict(lang_counts)
            job.blocks_skipped = lang_counts.get("en", 0) + lang_counts.get("unknown", 0)
            await session.commit()
            
            logger.info(f"Languages detected: {dict(lang_counts)}")
            
            # ===== STAGE 3: BATCH TRANSLATION =====
            job.status = DocumentStatus.TRANSLATING
            await session.commit()
            
            translated_count = 0
            total_to_translate = sum(len(b) for b in blocks_by_lang.values())
            
            # Pre-load models (cached)
            translator = get_cached_translator()
            tokenizer = get_cached_tokenizer()
            
            for lang, lang_blocks in blocks_by_lang.items():
                # Get NLLB source code
                source_nllb = lang_blocks[0].nllb_code if lang_blocks else "eng_Latn"
                
                # Process in batches
                for batch_start in range(0, len(lang_blocks), BATCH_SIZE):
                    batch_end = min(batch_start + BATCH_SIZE, len(lang_blocks))
                    batch = lang_blocks[batch_start:batch_end]
                    
                    # Batch translate
                    texts = [b.text for b in batch]
                    translations = translate_batch(
                        texts, source_nllb, job.target_lang,
                        translator, tokenizer
                    )
                    
                    # Apply translations
                    for block, translation in zip(batch, translations):
                        block.translated = translation
                        translated_count += 1
                    
                    # Update progress (less frequently)
                    if translated_count % PROGRESS_UPDATE_INTERVAL == 0:
                        job.processed_blocks = job.blocks_skipped + translated_count
                        job.progress = int((job.processed_blocks / job.total_blocks) * 100)
                        await session.commit()
            
            job.blocks_translated = translated_count
            
            # ===== STAGE 4: OUTPUT =====
            output = generate_output(blocks, job.output_format)
            
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
            
            logger.info(f"Document {job.id} completed in {job.processing_time_ms}ms")
            
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
            logger.error(f"Document {job_id} failed: {e}")
            job.status = DocumentStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            await session.commit()
            
            await log_audit_event(
                session, job_id, "document_failed",
                None, "failed", str(e), None
            )
            raise


def detect_languages_parallel(blocks) -> Tuple[List, Dict[str, int], Dict[str, List]]:
    """Detect languages using parallel processing."""
    from langdetect import detect
    from nllb_lang_codes import get_nllb_code
    
    lang_counts: Dict[str, int] = defaultdict(int)
    blocks_by_lang: Dict[str, List] = defaultdict(list)
    
    def detect_single(block):
        try:
            iso_code = detect(block.text)
            return block, iso_code
        except Exception:
            return block, "unknown"
    
    # Use thread pool for parallel detection
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(detect_single, blocks))
    
    for block, iso_code in results:
        lang_counts[iso_code] += 1
        
        if iso_code == "en" or iso_code == "unknown":
            block.translated = None
            block.lang = iso_code
        else:
            nllb_code = get_nllb_code(iso_code)
            block.lang = iso_code
            block.nllb_code = nllb_code or "eng_Latn"
            blocks_by_lang[iso_code].append(block)
    
    return blocks, lang_counts, blocks_by_lang


def translate_batch(
    texts: List[str],
    source_lang: str,
    target_lang: str,
    translator,
    tokenizer,
) -> List[str]:
    """Translate multiple texts in a single batch for efficiency."""
    if not texts:
        return []
    
    # Tokenize all texts
    tokenizer.src_lang = source_lang
    all_tokens = []
    for text in texts:
        tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(text))
        all_tokens.append(tokens)
    
    # Batch translate
    target_prefixes = [[target_lang]] * len(texts)
    results = translator.translate_batch(
        all_tokens,
        target_prefix=target_prefixes,
        beam_size=4,  # Reduced from 5 for speed
        max_batch_size=BATCH_SIZE,
    )
    
    # Decode all results
    translations = []
    for result in results:
        target_tokens = result.hypotheses[0][1:]  # Skip language token
        translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target_tokens))
        translations.append(translation)
    
    return translations


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
