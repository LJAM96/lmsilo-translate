"""
Translate Backend - FastAPI Application

Main entry point for the translation API with:
- REST API for translation jobs
- Model management (add/download/remove models)
- Celery integration for async processing
- NLLB-200 model for 200+ language translation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Translate API...")
    
    # Initialize database tables
    try:
        from services.database import init_db, Base, engine
        # Import models so they register with Base.metadata
        from models.database import Model
        from models.job import TranslationJob
        
        # Initialize local tables
        await init_db()
        
        # Import models to ensure tables are created
        from models.job import TranslationJob  # noqa
        from models.document import DocumentJob  # noqa
        
        # Try to init shared audit table
        try:
            import sys
            sys.path.insert(0, "/app")
            from shared.models.audit import AuditLog, Base as AuditBase
            async with engine.begin() as conn:
                await conn.run_sync(AuditBase.metadata.create_all)
            logger.info("Audit table initialized")
        except ImportError:
            logger.warning("Shared audit module not available")
        
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init skipped: {e}")
    
    yield
    logger.info("Shutting down Translate API...")


app = FastAPI(
    title="LMSilo Translate API",
    description="AI Translation service with pluggable model support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8083",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include model management routes
from api.models import router as models_router
app.include_router(models_router, prefix="/models", tags=["models"])

# Include job queue routes
from api.jobs import router as jobs_router
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

# Include document translation routes
from api.documents import router as documents_router
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])

# Include audit log routes
import sys
sys.path.insert(0, "/app")  # Add parent for shared imports
try:
    from shared.api.audit import create_audit_router
    from shared.services.audit import AuditLogger
    from services.database import get_session, async_session_maker
    audit_router = create_audit_router(get_session)
    app.include_router(audit_router, prefix="/api/audit", tags=["audit"])
    audit_logger = AuditLogger("translate")
except ImportError:
    logger.warning("Shared audit module not available")
    audit_logger = None


# Request/Response models
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if not provided)")
    target_lang: str = Field("eng_Latn", description="Target NLLB language code")


class TranslateResponse(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    translation: str


class BatchTranslateRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=1000)
    target_lang: str = Field("eng_Latn")


class BatchTranslateResponse(BaseModel):
    results: List[dict]
    count: int
    stats: dict


class LanguageInfo(BaseModel):
    code: str
    name: str
    nllb_code: str


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0", "model": "NLLB-200"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "LMSilo Translate API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/languages", response_model=List[LanguageInfo])
async def get_languages():
    """Get list of supported languages."""
    try:
        from .nllb_lang_codes import get_all_supported_languages
        languages = get_all_supported_languages()
        return [
            LanguageInfo(code=code, name=name, nllb_code=nllb)
            for code, (name, nllb) in languages.items()
        ]
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        # Return a minimal list if the full list isn't available
        return [
            LanguageInfo(code="en", name="English", nllb_code="eng_Latn"),
            LanguageInfo(code="es", name="Spanish", nllb_code="spa_Latn"),
            LanguageInfo(code="fr", name="French", nllb_code="fra_Latn"),
            LanguageInfo(code="de", name="German", nllb_code="deu_Latn"),
            LanguageInfo(code="zh", name="Chinese", nllb_code="zho_Hans"),
        ]


@app.post("/translate", response_model=TranslateResponse)
async def translate(request_data: TranslateRequest, request: Request):
    """Translate a single text."""
    import time
    start_time = time.time()
    
    try:
        # Import translation functions from the Flask app module
        from .app import translate_text_single, detect_language, get_nllb_code
        
        text = request_data.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is empty")
        
        # Auto-detect source language if not provided
        if request_data.source_lang:
            source_nllb = get_nllb_code(request_data.source_lang)
            if not source_nllb:
                raise HTTPException(status_code=400, detail=f"Unsupported source language: {request_data.source_lang}")
        else:
            iso_code, source_nllb = detect_language(text)
            if not source_nllb:
                raise HTTPException(status_code=400, detail="Could not detect source language")
        
        translation = translate_text_single(text, source_nllb, request_data.target_lang)
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log audit event for direct translation
        if audit_logger:
            try:
                async with async_session_maker() as session:
                    await audit_logger.log(
                        session=session,
                        action="direct_translation",
                        request=request,
                        processing_time_ms=processing_time_ms,
                        status="success",
                        metadata={
                            "source_lang": source_nllb,
                            "target_lang": request_data.target_lang,
                            "text_length": len(text),
                            "translation_length": len(translation),
                        },
                    )
            except Exception:
                pass  # Don't fail translation if audit fails
        
        return TranslateResponse(
            text=text,
            source_lang=source_nllb,
            target_lang=request_data.target_lang,
            translation=translation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate/batch", response_model=BatchTranslateResponse)
async def translate_batch(request: BatchTranslateRequest):
    """Translate a batch of texts."""
    try:
        from .app import translate_text_batch, detect_language, fast_language_check
        from collections import defaultdict
        
        results = []
        texts = request.texts
        target_lang = request.target_lang
        
        # Group by detected language
        lang_groups = defaultdict(list)
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results.append({"status": "skipped", "reason": "empty text", "index": i})
                continue
                
            quick = fast_language_check(text)
            if quick == 'english' and target_lang == 'eng_Latn':
                results.append({"status": "skipped", "reason": "already english", "index": i, "text": text})
                continue
                
            iso, nllb = detect_language(text)
            if not nllb:
                results.append({"status": "error", "error": f"Unsupported language: {iso}", "index": i})
                continue
                
            lang_groups[nllb].append((i, text))
        
        # Translate each language group
        for nllb_lang, items in lang_groups.items():
            indices = [i for i, _ in items]
            group_texts = [t for _, t in items]
            
            translations = translate_text_batch(group_texts, nllb_lang, target_lang)
            
            for idx, text, translation in zip(indices, group_texts, translations):
                results.append({
                    "status": "success",
                    "index": idx,
                    "source_lang": nllb_lang,
                    "text": text,
                    "translation": translation
                })
        
        # Sort by original index
        results.sort(key=lambda x: x.get("index", 0))
        
        stats = {
            "translated": sum(1 for r in results if r.get("status") == "success"),
            "skipped": sum(1 for r in results if r.get("status") == "skipped"),
            "errors": sum(1 for r in results if r.get("status") == "error"),
        }
        
        return BatchTranslateResponse(
            results=results,
            count=len(results),
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
