"""Model-related Pydantic schemas for translation with pluggable engine support."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Type of translation model."""
    TRANSLATION = "translation"


class ModelEngine(str, Enum):
    """
    Supported translation model engines.
    
    Users can upload models for any of these engines.
    """
    # CTranslate2-based NLLB (primary)
    NLLB_CT2 = "nllb-ct2"
    
    # Other potential engines for future
    OPUS = "opus"
    MARIAN = "marian"
    M2M100 = "m2m100"
    SEAMLESS = "seamless"


class ModelSource(str, Enum):
    """Where the model comes from."""
    HUGGINGFACE = "huggingface"
    LOCAL_UPLOAD = "local"
    URL = "url"
    BUILTIN = "builtin"


class ModelInfo(BaseModel):
    """Information about a model's capabilities."""
    
    size_mb: Optional[int] = Field(default=None, description="Model size in megabytes")
    languages: List[str] = Field(default=["multilingual"], description="Supported languages")
    description: str = Field(default="", description="Model description")
    recommended_vram_gb: Optional[float] = Field(default=None, description="Recommended VRAM in GB")
    num_languages: Optional[int] = Field(default=None, description="Number of supported languages")
    extra_config: Dict[str, Any] = Field(default_factory=dict, description="Engine-specific configuration")


class ModelCreate(BaseModel):
    """Schema for registering a new model."""
    
    name: str = Field(..., description="Model display name")
    model_type: ModelType = Field(default=ModelType.TRANSLATION, description="Type of model")
    engine: ModelEngine = Field(..., description="Processing engine for this model")
    
    # Model source
    source: ModelSource = Field(default=ModelSource.HUGGINGFACE, description="Where to get the model")
    model_id: str = Field(
        ...,
        description="Model identifier - HuggingFace repo ID, local path, or URL",
    )
    revision: Optional[str] = Field(default=None, description="HuggingFace revision/branch")
    
    # Configuration
    info: ModelInfo = Field(default_factory=ModelInfo, description="Model information")
    is_default: bool = Field(default=False, description="Set as default translation model")
    
    # Engine-specific options
    compute_type: Optional[str] = Field(
        default=None,
        description="Compute type: float16, int8, float32",
    )
    device: Optional[str] = Field(
        default=None,
        description="Override device: cuda, cpu, auto",
    )


class ModelResponse(BaseModel):
    """Schema for model response."""
    
    id: str = Field(..., description="Unique model ID")
    name: str
    model_type: ModelType
    engine: ModelEngine
    source: ModelSource
    model_id: str
    revision: Optional[str] = None
    
    info: ModelInfo
    is_default: bool
    compute_type: Optional[str] = None
    device: Optional[str] = None
    
    # Status
    is_downloaded: bool = Field(default=False, description="Whether model is downloaded locally")
    download_progress: Optional[float] = Field(
        default=None,
        description="Download progress percentage if currently downloading",
    )
    local_path: Optional[str] = Field(default=None, description="Local file path if downloaded")
    
    # Timestamps
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ModelDownloadRequest(BaseModel):
    """Request to download a model."""
    
    model_id: str = Field(..., description="Model ID to download")
    force: bool = Field(default=False, description="Force re-download even if exists")


# Pre-defined NLLB models (CTranslate2 format)
BUILTIN_MODELS: Dict[ModelEngine, Dict[str, ModelInfo]] = {
    ModelEngine.NLLB_CT2: {
        # Distilled models (faster, smaller)
        "nllb-200-distilled-600M": ModelInfo(
            size_mb=1200,
            description="Distilled 600M - Fast, good quality for common languages.",
            recommended_vram_gb=2.0,
            num_languages=200,
        ),
        "nllb-200-distilled-1.3B": ModelInfo(
            size_mb=2600,
            description="Distilled 1.3B - Good balance of speed and quality.",
            recommended_vram_gb=4.0,
            num_languages=200,
        ),
        # Full models
        "nllb-200-1.3B": ModelInfo(
            size_mb=5200,
            description="Full 1.3B - High quality translation.",
            recommended_vram_gb=6.0,
            num_languages=200,
        ),
        "nllb-200-3.3B": ModelInfo(
            size_mb=13000,
            description="Full 3.3B - Best quality, requires significant resources.",
            recommended_vram_gb=12.0,
            num_languages=200,
        ),
    },
    # OPUS models for future
    ModelEngine.OPUS: {
        "opus-mt-en-ROMANCE": ModelInfo(
            size_mb=300,
            description="English to Romance languages (es, fr, it, pt, ro).",
            recommended_vram_gb=1.0,
            num_languages=5,
        ),
    },
}


# HuggingFace model IDs for each builtin
BUILTIN_HF_IDS: Dict[str, str] = {
    "nllb-200-distilled-600M": "facebook/nllb-200-distilled-600M",
    "nllb-200-distilled-1.3B": "facebook/nllb-200-distilled-1.3B", 
    "nllb-200-1.3B": "facebook/nllb-200-1.3B",
    "nllb-200-3.3B": "facebook/nllb-200-3.3B",
    "opus-mt-en-ROMANCE": "Helsinki-NLP/opus-mt-en-ROMANCE",
}


def get_engines() -> List[ModelEngine]:
    """Get all available translation engines."""
    return list(ModelEngine)
