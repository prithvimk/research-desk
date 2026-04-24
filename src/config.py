import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use absolute paths to avoid Windows pathing issues
BASE_DIR = Path(__file__).parent.parent

# Paths
INBOX_DIR = BASE_DIR / os.getenv("INBOX_PATH", "data/01_inbox").lstrip("./")
VAULT_DIR = BASE_DIR / os.getenv("VAULT_PATH", "data/04_obsidian_vault").lstrip("./")
PROCESSED_DIR = BASE_DIR / os.getenv("PROCESSED_PATH", "data/02_processed").lstrip("./")

# LLM / Model Config
LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:11434/v1/chat/completions")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemma4:e2b")
MAX_CONTEXT_TOKENS = int(os.getenv("LLM_MAX_CONTEXT_TOKENS", "4096"))
CHUNK_SIZE = int(os.getenv("LLM_CHUNK_SIZE", "3000"))
CHUNK_OVERLAP = int(os.getenv("LLM_CHUNK_OVERLAP", "300"))