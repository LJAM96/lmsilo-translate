"""
Celery worker for async PDF translation processing.

This enables:
- Non-blocking uploads (instant response with job ID)
- Real-time progress tracking
- Multiple concurrent jobs
- Horizontal scaling with multiple workers

Usage:
    celery -A celery_worker.celery_app worker --loglevel=info --concurrency=2
"""

import os
import io
import time
import logging
import sys
from celery import Celery
from celery.exceptions import Ignore

# Configure logging to match app.py format
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'translation_worker',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=86400,  # 24 hours max
    task_soft_time_limit=82800,  # 23 hours soft limit
    worker_prefetch_multiplier=1,  # Don't prefetch tasks (long-running)
    result_expires=86400,  # Results expire after 24 hours
)


# Import translation functions (lazy import to avoid loading model in main process)
_translator_loaded = False
_process_pdf_func = None


def _ensure_translator_loaded():
    """Lazy load the translation model only when needed."""
    global _translator_loaded, _process_pdf_func
    
    if not _translator_loaded:
        logger.info("Loading translation model in worker...")
        
        # Import from app module
        from app import process_pdf
        
        _process_pdf_func = process_pdf
        _translator_loaded = True
        
        logger.info("Translation model loaded successfully")


@celery_app.task(bind=True, name='process_pdf_async')
def process_pdf_async(self, job_id, input_path, filename, output_format='overlay'):
    """
    Async PDF translation task with progress updates.
    
    Args:
        job_id: Job id (also used as Celery task id)
        input_path: Path to the uploaded PDF on shared storage
        filename: Original filename
        output_format: 'overlay' or 'annotated'
        target_lang: NLLB target language code
    
    Returns:
        dict with status and output path
    """
    try:
        _ensure_translator_loaded()
        
        # Read PDF from disk (shared volume) to avoid pushing large blobs through Redis
        with open(input_path, "rb") as f:
            file_content = f.read()
        
        logger.info(f"Starting async PDF processing: {filename}")
        
        # Update state to PROCESSING
        self.update_state(
            state='PROCESSING',
            meta={
                'status': 'Starting PDF processing...',
                'filename': filename,
                'progress': 0
            }
        )
        
        start_time = time.time()
        
        # Process PDF using optimized function (hardcoded output is English)
        result_file = _process_pdf_func(file_content, filename, output_format, job_id=job_id)
        
        processing_time = time.time() - start_time
        
        from app import ASYNC_STORAGE_DIR
        os.makedirs(ASYNC_STORAGE_DIR, exist_ok=True)
        output_path = os.path.join(ASYNC_STORAGE_DIR, f"{job_id}.output.pdf")
        with open(output_path, "wb") as f:
            f.write(result_file.getvalue())
        
        logger.info(f"PDF processing complete: {filename} in {processing_time:.2f}s")
        
        return {
            'status': 'complete',
            'filename': filename,
            'processing_time_seconds': round(processing_time, 2),
            'output_path': output_path,
            'file_size_bytes': len(result_file.getvalue()),
        }
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'error': str(e)
            }
        )
        raise Ignore()


@celery_app.task(bind=True, name='translate_batch_async')
def translate_batch_async(self, texts, target_lang='eng_Latn'):
    """
    Async batch translation task.
    
    Args:
        texts: List of texts to translate
        target_lang: Target language code
    
    Returns:
        dict with translation results
    """
    try:
        _ensure_translator_loaded()
        
        from app import fast_language_check, detect_language, translate_text_batch, metrics, DETECT_WORKERS
        from collections import defaultdict
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        logger.info(f"Starting async batch translation: {len(texts)} texts")
        
        self.update_state(
            state='PROCESSING',
            meta={
                'status': 'Detecting languages...',
                'total': len(texts),
                'current': 0,
                'progress': 0
            }
        )
        
        start_time = time.time()
        results = [None] * len(texts)
        
        # Parallel language detection
        def detect_text_lang(idx, text):
            if not text or not isinstance(text, str) or len(text.strip()) < 2:
                return idx, 'empty', None, None
            quick = fast_language_check(text)
            if quick == 'english':
                return idx, 'english', 'en', None
            if quick == 'empty':
                return idx, 'empty', None, None
            iso, nllb = detect_language(text[:500])
            if iso == 'en':
                return idx, 'english', 'en', None
            return idx, 'foreign', iso, nllb
        
        lang_results = {}
        with ThreadPoolExecutor(max_workers=max(1, int(DETECT_WORKERS))) as executor:
            futures = {executor.submit(detect_text_lang, i, t): i for i, t in enumerate(texts)}
            for future in as_completed(futures):
                idx, status, iso, nllb = future.result()
                lang_results[idx] = (status, iso, nllb)
        
        # Group by language
        lang_groups = defaultdict(list)
        for idx, text in enumerate(texts):
            status, iso, nllb = lang_results[idx]
            if status == 'empty':
                results[idx] = {"status": "skipped", "reason": "empty text"}
            elif status == 'english':
                results[idx] = {"status": "skipped", "reason": "source is english"}
            elif nllb:
                lang_groups[nllb].append((idx, text))
            else:
                results[idx] = {"status": "error", "error": f"Unsupported language: {iso}"}
        
        self.update_state(
            state='PROCESSING',
            meta={
                'status': 'Translating...',
                'total': len(texts),
                'current': len([r for r in results if r]),
                'progress': int(len([r for r in results if r]) / len(texts) * 100)
            }
        )
        
        # Batch translate each language group
        completed = len([r for r in results if r])
        for nllb_lang, items in lang_groups.items():
            indices = [i for i, _ in items]
            group_texts = [t for _, t in items]
            
            try:
                translations = translate_text_batch(group_texts, nllb_lang, target_lang)
                for idx, translation in zip(indices, translations):
                    results[idx] = {
                        "status": "success",
                        "source_lang": nllb_lang.split('_')[0],
                        "translation": translation
                    }
                    completed += 1
                
                # Update progress
                self.update_state(
                    state='PROCESSING',
                    meta={
                        'status': f'Translated {completed}/{len(texts)}',
                        'total': len(texts),
                        'current': completed,
                        'progress': int(completed / len(texts) * 100)
                    }
                )
                
            except Exception as e:
                logger.error(f"Batch translation error for {nllb_lang}: {e}")
                for idx in indices:
                    results[idx] = {"status": "error", "error": str(e)}
        
        processing_time = time.time() - start_time
        
        successful = sum(1 for r in results if r and r.get("status") == "success")
        skipped = sum(1 for r in results if r and r.get("status") == "skipped")
        errors = sum(1 for r in results if r and r.get("status") == "error")
        
        logger.info(f"Batch translation complete: {successful} translated, {skipped} skipped, {errors} errors")
        
        return {
            'status': 'complete',
            'results': results,
            'count': len(results),
            'stats': {
                'translated': successful,
                'skipped': skipped,
                'errors': errors,
                'processing_time_seconds': round(processing_time, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Batch translation failed: {e}")
        self.update_state(
            state='FAILURE',
            meta={'status': 'failed', 'error': str(e)}
        )
        raise Ignore()


if __name__ == '__main__':
    celery_app.start()
