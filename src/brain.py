import requests
from config import LLM_API_URL, MODEL_NAME
from logger import get_logger
from prompt_manager import load_prompt

logger = get_logger(__name__)

class ResearchBrain:
    def __init__(self):
        self.url = LLM_API_URL

    def process_chunk(self, text_chunk: str, prompt_config: dict) -> dict:
        """Generic method to process text with a given prompt configuration."""
        system_prompt = prompt_config.get("prompt", "")
        temperature = prompt_config.get("temperature", 0.1)  # Default fallback
        top_k = prompt_config.get("top_k", 40)              # Default fallback
        
        payload = {
            "model": MODEL_NAME, # llama.cpp usually ignores this if -m is used, but it's safe to include for standard OpenAI spec
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_chunk}
            ],
            "temperature": temperature,
            "top_k": top_k
        }

        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            
            # Adjust based on standard OpenAI API format
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            
            logger.info(f"Brain processed chunk successfully using model {MODEL_NAME}.")
            return {"content": content}
            
        except Exception as e:
            logger.error(f"Server Error: {e}")
            return {"error": str(e)}

    def generate_note(self, text_chunk: str) -> dict:
        """Specific method to generate structured notes."""
        try:
            prompt_config = load_prompt("note_synthesis.yaml")
            user_message = f"You are processing ONE CHUNK of a larger document.\n\nFollow all instructions and strictly use the provided template.\n\nCHUNK:\n{text_chunk}"
            return self.process_chunk(user_message, prompt_config)
        except Exception as e:
            logger.error(f"Error generating note: {e}")
            return {"error": str(e)}