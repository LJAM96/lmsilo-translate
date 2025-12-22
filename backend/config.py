"""Configuration for Translate service."""

import os
from pathlib import Path


class Settings:
    """Application settings."""
    
    # Database (shared PostgreSQL)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres:5432/lmsilo"
    )
    
    # Redis (shared)
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Model storage
    model_dir: Path = Path(os.getenv("MODEL_DIR", "/app/models"))
    
    # Device settings
    device: str = os.getenv("DEVICE", "auto")
    compute_type: str = os.getenv("COMPUTE_TYPE", "auto")
    
    # HuggingFace
    hf_token: str = os.getenv("HF_TOKEN", "")
    hf_home: str = os.getenv("HF_HOME", "/app/models/huggingface")
    
    # Uploads
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
    max_text_length: int = int(os.getenv("MAX_TEXT_LENGTH", "50000"))


settings = Settings()

# Ensure directories exist
settings.model_dir.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
