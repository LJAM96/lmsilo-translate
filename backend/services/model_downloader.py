"""Model downloader service for translation engines."""

from pathlib import Path
from typing import Optional, Callable

from schemas.model import ModelEngine, ModelSource


async def download_model_for_engine(
    engine: ModelEngine,
    model_id: str,
    source: ModelSource,
    revision: Optional[str],
    target_dir: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """
    Download a model based on its engine and source.
    
    Returns the local path where the model is stored.
    """
    if source == ModelSource.HUGGINGFACE:
        return await download_from_huggingface(
            model_id=model_id,
            engine=engine,
            revision=revision,
            target_dir=target_dir,
            progress_callback=progress_callback,
        )
    elif source == ModelSource.URL:
        return await download_from_url(
            url=model_id,
            target_dir=target_dir,
            progress_callback=progress_callback,
        )
    elif source == ModelSource.LOCAL_UPLOAD:
        # Already local, just verify it exists
        path = Path(model_id)
        if not path.exists():
            raise ValueError(f"Local model not found: {model_id}")
        return path
    elif source == ModelSource.BUILTIN:
        # Download from HuggingFace using known IDs
        return await download_builtin_model(
            engine=engine,
            model_id=model_id,
            target_dir=target_dir,
            progress_callback=progress_callback,
        )
    else:
        raise ValueError(f"Unknown model source: {source}")


async def download_from_huggingface(
    model_id: str,
    engine: ModelEngine,
    revision: Optional[str],
    target_dir: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """Download translation model from HuggingFace Hub."""
    from huggingface_hub import snapshot_download
    
    # Create engine-specific directory
    engine_dir = target_dir / engine.value
    engine_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize model name for directory
    safe_name = model_id.replace("/", "_")
    model_dir = engine_dir / safe_name
    
    if progress_callback:
        progress_callback(10)
    
    # Download based on engine type
    if engine == ModelEngine.NLLB_CT2:
        # For NLLB models, check for pre-converted CT2 version
        ct2_repo_id = get_ct2_repo_id(model_id)
        
        if ct2_repo_id:
            # Download pre-converted CT2 model
            local_path = snapshot_download(
                repo_id=ct2_repo_id,
                revision=revision,
                local_dir=str(model_dir),
            )
        else:
            # Download original (may need conversion at load time)
            local_path = snapshot_download(
                repo_id=model_id,
                revision=revision,
                local_dir=str(model_dir),
            )
    elif engine in [ModelEngine.OPUS, ModelEngine.MARIAN]:
        # Helsinki-NLP OPUS/Marian models
        local_path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=str(model_dir),
        )
    elif engine == ModelEngine.M2M100:
        # Facebook M2M100 models
        local_path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=str(model_dir),
        )
    elif engine == ModelEngine.SEAMLESS:
        # SeamlessM4T models
        local_path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=str(model_dir),
        )
    else:
        # Generic HF download
        local_path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=str(model_dir),
        )
    
    if progress_callback:
        progress_callback(100)
    
    return Path(local_path)


def get_ct2_repo_id(model_id: str) -> Optional[str]:
    """Get CTranslate2-converted repo ID if available."""
    # Map of known CT2-converted NLLB models
    ct2_models = {
        "facebook/nllb-200-distilled-600M": "JustFrederik/nllb-200-distilled-600M-ct2-float16",
        "facebook/nllb-200-distilled-1.3B": "JustFrederik/nllb-200-distilled-1.3B-ct2-float16",
        "facebook/nllb-200-1.3B": "JustFrederik/nllb-200-1.3B-ct2-float16",
        "facebook/nllb-200-3.3B": "JustFrederik/nllb-200-3.3B-ct2-float16",
    }
    return ct2_models.get(model_id)


async def download_from_url(
    url: str,
    target_dir: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """Download model from direct URL."""
    import aiohttp
    from urllib.parse import urlparse
    
    # Get filename from URL
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    
    output_path = target_dir / "url_models" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total > 0 and progress_callback:
                        progress_callback(downloaded / total * 100)
    
    return output_path


async def download_builtin_model(
    engine: ModelEngine,
    model_id: str,
    target_dir: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """Download built-in models using known HuggingFace IDs."""
    from schemas.model import BUILTIN_HF_IDS
    
    hf_id = BUILTIN_HF_IDS.get(model_id)
    if not hf_id:
        raise ValueError(f"Unknown builtin model: {model_id}")
    
    return await download_from_huggingface(
        model_id=hf_id,
        engine=engine,
        revision=None,
        target_dir=target_dir,
        progress_callback=progress_callback,
    )
