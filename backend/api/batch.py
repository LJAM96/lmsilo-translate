"""
Batch import implementation for Translate service.

Provides CSV-based import for translation jobs (text-based, not file-based).
"""

from pathlib import Path
from typing import Dict, Any, List
from uuid import UUID, uuid4
from dataclasses import dataclass
import csv
import json
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TextBatchItem(BaseModel):
    """Single text item for batch translation."""
    text: str
    source_lang: str | None = None
    target_lang: str
    options: Dict[str, Any] | None = None


class TextBatchRequest(BaseModel):
    """Request for text-based batch translation."""
    items: List[TextBatchItem]


class TextBatchResponse(BaseModel):
    """Response for batch translation."""
    batch_id: str
    total_items: int
    status: str


class TranslateBatchImporter:
    """
    Batch importer for Translate service.
    
    Unlike Locate/Transcribe, Translate works with text, not files.
    Supports CSV import with format:
        text,source_lang,target_lang
        "Hello world",,fra_Latn
        "Goodbye",eng_Latn,deu_Latn
    """
    
    def __init__(self):
        self.service_name = "translate"
        self.max_items = 1000
        self._batches: Dict[str, Any] = {}
    
    def parse_csv(self, content: str) -> List[TextBatchItem]:
        """
        Parse CSV content into text batch items.
        
        Expected CSV format:
            text,source_lang,target_lang,options
            "Hello world",,fra_Latn,
            "Goodbye",eng_Latn,deu_Latn,
        """
        items = []
        reader = csv.DictReader(content.splitlines())
        
        for idx, row in enumerate(reader):
            if idx >= self.max_items:
                logger.warning(f"Batch limit reached ({self.max_items}), truncating")
                break
            
            text = row.get("text", "").strip()
            if not text:
                continue
            
            target_lang = row.get("target_lang", "").strip()
            if not target_lang:
                continue
            
            source_lang = row.get("source_lang", "").strip() or None
            
            # Parse options if present
            options_str = row.get("options", "").strip()
            options = None
            if options_str:
                try:
                    options = json.loads(options_str)
                except json.JSONDecodeError:
                    pass
            
            items.append(TextBatchItem(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                options=options,
            ))
        
        return items
    
    async def process_batch(
        self,
        batch_id: str,
        items: List[TextBatchItem],
        session: Any,
    ):
        """Process batch translation."""
        from models.job import TranslationJob
        from workers.tasks import process_translation
        
        results = []
        
        for idx, item in enumerate(items):
            try:
                # Create job
                job = TranslationJob(
                    id=uuid4(),
                    text=item.text,
                    source_lang=item.source_lang,
                    target_lang=item.target_lang,
                    status="pending",
                )
                
                session.add(job)
                await session.commit()
                await session.refresh(job)
                
                # Queue for processing
                process_translation.delay(str(job.id))
                
                results.append({
                    "index": idx,
                    "job_id": str(job.id),
                    "status": "queued",
                })
                
            except Exception as e:
                logger.error(f"Failed to create translation job: {e}")
                results.append({
                    "index": idx,
                    "status": "error",
                    "error": str(e),
                })
        
        self._batches[batch_id] = {
            "status": "completed",
            "results": results,
        }
        
        return results
    
    def create_router(self, get_session) -> APIRouter:
        """Create FastAPI router for batch endpoints."""
        router = APIRouter()
        
        @router.post("/csv", response_model=TextBatchResponse)
        async def import_from_csv(
            background_tasks: BackgroundTasks,
            file: UploadFile = File(...),
            session = Depends(get_session),
        ):
            """
            Import batch from CSV file.
            
            CSV format:
            ```
            text,source_lang,target_lang
            "Hello world",,fra_Latn
            "Goodbye",eng_Latn,deu_Latn
            ```
            """
            content = (await file.read()).decode("utf-8")
            items = self.parse_csv(content)
            
            if not items:
                raise HTTPException(status_code=400, detail="No valid items found in CSV")
            
            batch_id = str(uuid4())
            
            background_tasks.add_task(
                self.process_batch,
                batch_id,
                items,
                session,
            )
            
            return TextBatchResponse(
                batch_id=batch_id,
                total_items=len(items),
                status="processing",
            )
        
        @router.post("/texts", response_model=TextBatchResponse)
        async def import_texts(
            request: TextBatchRequest,
            background_tasks: BackgroundTasks,
            session = Depends(get_session),
        ):
            """Import batch from JSON array of texts."""
            if len(request.items) > self.max_items:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too many items ({len(request.items)}), max is {self.max_items}"
                )
            
            batch_id = str(uuid4())
            
            background_tasks.add_task(
                self.process_batch,
                batch_id,
                request.items,
                session,
            )
            
            return TextBatchResponse(
                batch_id=batch_id,
                total_items=len(request.items),
                status="processing",
            )
        
        @router.get("/{batch_id}")
        async def get_batch_status(batch_id: str):
            """Get batch status."""
            batch = self._batches.get(batch_id)
            if not batch:
                raise HTTPException(status_code=404, detail="Batch not found")
            return batch
        
        return router


# Create singleton instance
translate_batch_importer = TranslateBatchImporter()
