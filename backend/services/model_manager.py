"""
Model Manager with Idle Timeout Unloading

Manages translation models with automatic unloading after idle period
to save RAM/VRAM when not in use.
"""

import os
import time
import threading
import logging
import gc
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Default idle timeout: 10 minutes
DEFAULT_IDLE_TIMEOUT = int(os.getenv("MODEL_IDLE_TIMEOUT", "600"))


class ModelManager:
    """
    Thread-safe model manager with idle timeout unloading.
    
    Models are loaded on first use and automatically unloaded
    after the specified idle timeout period.
    """
    
    def __init__(self, idle_timeout: int = DEFAULT_IDLE_TIMEOUT):
        self._model: Optional[Any] = None
        self._tokenizer: Optional[Any] = None
        self._last_used: float = 0
        self._timeout = idle_timeout
        self._lock = threading.RLock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = True
        
        # Start background cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"ModelManager initialized with {idle_timeout}s idle timeout")
    
    def _start_cleanup_thread(self):
        """Start background thread to check for idle timeout."""
        def cleanup_loop():
            while self._running:
                time.sleep(60)  # Check every minute
                self._check_timeout()
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def _check_timeout(self):
        """Check if model should be unloaded due to idle timeout."""
        with self._lock:
            if self._model is not None and self._last_used > 0:
                idle_time = time.time() - self._last_used
                if idle_time > self._timeout:
                    logger.info(f"Model idle for {idle_time:.0f}s, unloading to save memory")
                    self._unload_model()
    
    def _unload_model(self):
        """Unload the model and free memory."""
        self._model = None
        self._tokenizer = None
        self._last_used = 0
        
        # Force garbage collection
        gc.collect()
        
        # Try to clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Cleared CUDA cache")
        except ImportError:
            pass
        
        logger.info("Model unloaded successfully")
    
    def _load_model(self):
        """Load the translation model (override in subclass or set loader)."""
        raise NotImplementedError("Subclass must implement _load_model")
    
    def get_model(self):
        """
        Get the model, loading it if necessary.
        Updates last-used timestamp for idle tracking.
        """
        with self._lock:
            self._last_used = time.time()
            
            if self._model is None:
                logger.info("Loading model...")
                start = time.time()
                self._load_model()
                logger.info(f"Model loaded in {time.time() - start:.1f}s")
            
            return self._model
    
    def get_tokenizer(self):
        """Get the tokenizer, loading model if necessary."""
        with self._lock:
            self._last_used = time.time()
            if self._tokenizer is None:
                self._load_model()
            return self._tokenizer
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self._model is not None
    
    @property
    def idle_seconds(self) -> float:
        """Get seconds since last use."""
        if self._last_used == 0:
            return 0
        return time.time() - self._last_used
    
    def shutdown(self):
        """Shutdown the manager and unload model."""
        self._running = False
        with self._lock:
            if self._model is not None:
                self._unload_model()


class TranslationModelManager(ModelManager):
    """Model manager specifically for NLLB translation models."""
    
    def __init__(self, model_path: str = None, idle_timeout: int = DEFAULT_IDLE_TIMEOUT):
        self._model_path = model_path
        super().__init__(idle_timeout)
    
    def _load_model(self):
        """Load the CTranslate2 translation model."""
        import ctranslate2
        from transformers import AutoTokenizer
        
        model_name = self._model_path or "facebook/nllb-200-distilled-600M"
        
        # Try CT2 converted model first
        ct2_path = f"/app/models/{model_name.split('/')[-1]}-ct2"
        
        if os.path.exists(ct2_path):
            logger.info(f"Loading CT2 model from {ct2_path}")
            self._model = ctranslate2.Translator(
                ct2_path,
                device="cuda" if os.getenv("DEVICE", "auto") == "cuda" else "cpu",
                compute_type="auto"
            )
        else:
            # Fall back to HuggingFace with on-the-fly conversion
            logger.info(f"Loading model from HuggingFace: {model_name}")
            self._model = ctranslate2.Translator(
                model_name,
                device="cuda" if os.getenv("DEVICE", "auto") == "cuda" else "cpu",
                compute_type="auto"
            )
        
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info(f"Translation model loaded: {model_name}")


# Global singleton instance
_manager: Optional[TranslationModelManager] = None


def get_model_manager() -> TranslationModelManager:
    """Get or create the global model manager instance."""
    global _manager
    if _manager is None:
        _manager = TranslationModelManager()
    return _manager
