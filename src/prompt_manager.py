import os
import yaml
from pathlib import Path

# Use the parent directory of 'src' as the base for finding 'prompts'
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

def load_prompt(prompt_filename: str) -> dict:
    """
    Loads a prompt from a YAML file in the prompts directory.
    Returns a dictionary containing the prompt text and metadata.
    """
    prompt_path = PROMPTS_DIR / prompt_filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
    with open(prompt_path, 'r', encoding='utf-8') as f:
        if prompt_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            # Fallback for old text files if any
            return {"prompt": f.read()}
