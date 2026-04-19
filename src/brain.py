import ollama
import re
from config import MODEL_NAME, MAX_CONTEXT_TOKENS

class ResearchBrain:
    def __init__(self):
        self.model = MODEL_NAME

    def generate_note(self, text_chunk):
        system_prompt = f"""
        You are a research assistant. Extract key entities and concepts from this text.
        Format as a Karpathy-style Obsidian wiki note.
        Target context: {MAX_CONTEXT_TOKENS} tokens.
        Use [[WikiLinks]] for internal connections.
        """
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=f"Text to analyze: {text_chunk}",
                system=system_prompt,
                options={
                    "num_ctx": MAX_CONTEXT_TOKENS,
                    "temperature": 0.1,  # Keep it factual
                    "num_gpu": 1        # Ensure it stays on the 1050Ti
                }
            )
            
            full_response = response['response']
            
            # Gemma 4 Thinking Extraction
            thought = re.search(r'<\|think\|>(.*?)<\|thought\|>', full_response, re.DOTALL)
            clean_content = re.sub(r'<\|think\|>.*?<\|thought\|>', '', full_response, flags=re.DOTALL).strip()
            
            return {
                "thought": thought.group(1) if thought else "No trace",
                "content": clean_content
            }
        except Exception as e:
            return {"error": str(e)}