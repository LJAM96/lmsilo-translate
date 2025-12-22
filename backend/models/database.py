"""Database models for translation service."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, JSON, Enum as SQLEnum
from services.database import Base
from schemas.model import ModelType, ModelEngine, ModelSource


def generate_uuid():
    return str(uuid.uuid4())


class Model(Base):
    """Translation model registry."""
    
    __tablename__ = "translate_models"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    model_type = Column(SQLEnum(ModelType), nullable=False, default=ModelType.TRANSLATION)
    engine = Column(SQLEnum(ModelEngine), nullable=False)
    source = Column(SQLEnum(ModelSource), nullable=False, default=ModelSource.HUGGINGFACE)
    model_id = Column(String, nullable=False)  # HF repo ID, local path, or URL
    revision = Column(String, nullable=True)
    
    # Model configuration
    info = Column(JSON, default=dict)
    compute_type = Column(String, nullable=True)
    device = Column(String, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_downloaded = Column(Boolean, default=False)
    download_progress = Column(Float, nullable=True)
    local_path = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Model {self.name} ({self.engine.value})>"
