"""Job schemas for Translate queue system."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranslationJobCreate(BaseModel):
    """Request to create a translation job."""
    text: str = Field(..., min_length=1, max_length=50000)
    source_lang: Optional[str] = Field(default=None, description="Auto-detect if null")
    target_lang: str = Field(..., description="NLLB language code")
    model_id: Optional[UUID] = Field(default=None, description="Specific model to use")


class TranslationJobResponse(BaseModel):
    """Translation job response."""
    id: UUID
    status: JobStatus
    text: str
    source_lang: Optional[str]
    target_lang: str
    translation: Optional[str] = None
    error: Optional[str] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchTranslationJobCreate(BaseModel):
    """Request to create a batch translation job."""
    texts: List[str] = Field(..., min_length=1, max_length=100)
    source_lang: Optional[str] = None
    target_lang: str
