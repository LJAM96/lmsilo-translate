from huggingface_hub import snapshot_download
import os

# Model: Pre-converted CTranslate2 INT8 model
MODEL_NAME = "OpenNMT/nllb-200-3.3B-ct2-int8"
CACHE_DIR = "/app/models"

print(f"Pre-downloading model: {MODEL_NAME} to {CACHE_DIR}...")
snapshot_download(MODEL_NAME, cache_dir=CACHE_DIR)
print("Model download complete.")
