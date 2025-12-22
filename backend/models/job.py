"""Job model for Translate queue system."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from services.database import Base


class TranslationJob(Base):
    """Translation job model for shared workspace."""
    
    __tablename__ = "translate_jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Input
    text: Mapped[str] = mapped_column(Text)
    source_lang: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    target_lang: Mapped[str] = mapped_column(String(20))
    detected_lang: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Output
    translation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Model info
    model_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "source_lang": self.detected_lang or self.source_lang,
            "target_lang": self.target_lang,
            "translation": self.translation,
            "status": self.status,
            "error": self.error,
            "model_used": self.model_name,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
