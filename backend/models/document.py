"""Document job model for translation queue."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID

from models.database import Base


class DocumentStatus(str, Enum):
    """Document job status."""
    PENDING = "pending"
    EXTRACTING = "extracting"
    DETECTING = "detecting"
    TRANSLATING = "translating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentJob(Base):
    """
    Document translation job model.
    
    Tracks document upload, processing status, and results.
    Visible to all users in shared workspace.
    """
    __tablename__ = "document_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # xxHash3
    file_size_bytes = Column(Integer, nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, txt, etc.
    
    # Processing status
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    total_blocks = Column(Integer, default=0)
    processed_blocks = Column(Integer, default=0)
    
    # Language stats
    languages_found = Column(JSON, default=dict)  # {"en": 50, "es": 30, "fr": 20}
    blocks_skipped = Column(Integer, default=0)  # English blocks skipped
    blocks_translated = Column(Integer, default=0)
    
    # Target language
    target_lang = Column(String(20), default="eng_Latn")
    
    # Results
    output_path = Column(String(500), nullable=True)
    output_format = Column(String(10), default="json")  # json, csv
    
    # Error handling
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "filename": self.original_filename,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "total_blocks": self.total_blocks,
            "processed_blocks": self.processed_blocks,
            "languages_found": self.languages_found,
            "blocks_skipped": self.blocks_skipped,
            "blocks_translated": self.blocks_translated,
            "target_lang": self.target_lang,
            "output_format": self.output_format,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_ms": self.processing_time_ms,
        }
