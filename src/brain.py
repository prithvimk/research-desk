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
                    "content": """You are an expert knowledge architect converting document chunks into structured Obsidian notes.

You MUST strictly follow the output template provided below.

--- HARD CONSTRAINTS ---
- Do NOT change the template structure
- Do NOT add extra sections
- Do NOT omit sections
- Fill every field (use "N/A" if needed)

- Output ONLY valid Obsidian markdown
- Separate notes using: ===NOTE===

--- TEMPLATE START ---

---
title: {{Title}}
type: {{concept | process | entity | metric | framework}}
source: {{document_name}}
chunk_id: {{chunk_id}}
created: {{date}}
tags: [{{tag1}}, {{tag2}}]
status: {{complete | incomplete}}
---

# {{Title}}

## 🧠 Summary
{{summary}}

## 📌 Key Points
- 
- 

## 🔍 Details
{{content}}

## 🔗 Related Concepts
- [[...]]
- [[...]]

## 📊 Data / Facts
- 

## ❗ Context Status
{{Explain if this note seems partial or complete}}

## 🧾 Source Snippet
> {{excerpt}}

--- TEMPLATE END ---"""
                },
                {
                    "role": "user", 
                    "content": f"""You are processing ONE CHUNK of a larger document.

Follow all instructions and strictly use the provided template.

CHUNK:
{text_chunk}"""
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