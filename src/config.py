import os
from pathlib import Path

# Use absolute paths to avoid Windows pathing issues
BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "data/01_inbox"
VAULT_DIR = BASE_DIR / "data/04_obsidian_vault"

# GPU Strategy: 4GB VRAM limits
MODEL_NAME = "gemma4:e2b"
MAX_CONTEXT_TOKENS = 4096  # Safe for 1050Ti to prevent swapping
CHUNK_SIZE = 3000          # Leave room for the model's response
CHUNK_OVERLAP = 300