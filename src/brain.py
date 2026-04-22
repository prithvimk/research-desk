import requests
import json
import re
from config import logger

class ResearchBrain:
    def __init__(self):
        self.url = "http://127.0.0.1:8080/v1/chat/completions"

    def generate_note(self, text_chunk):
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a Research Assistant. Extract technical entities and concepts. Format as Obsidian notes with [[WikiLinks]]."
                },
                {
                    "role": "user", 
                    "content": f"Analyze this text: {text_chunk}"
                }
            ],
            "temperature": 0.1,
            "extra_body": {"top_k": 40} # Granite 4 specific tuning
        }

        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            
            # Logging the performance (llama-server returns this in headers/meta)
            logger.info("🧠 Brain processed chunk via Speculative Decoding.")
            return {"content": content}
            
        except Exception as e:
            logger.error(f"❌ Server Error: {e}")
            return {"error": str(e)}