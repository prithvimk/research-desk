import time
import os
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter
from brain import ResearchBrain
from config import INBOX_DIR, VAULT_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from logger import get_logger

logger = get_logger(__name__)

class ResearchHandler(FileSystemEventHandler):
    def __init__(self):
        self.brain = ResearchBrain()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def on_created(self, event):
        if event.is_directory or not (event.src_path.endswith(".txt") or event.src_path.endswith(".md")):
            return
        
        logger.info(f"Processing: {os.path.basename(event.src_path)}")
        self.process_file(event.src_path)

    def process_file(self, file_path):
        start_time = time.time()
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        # Split long papers into GPU-friendly chunks
        chunks = self.splitter.split_text(raw_text)
        logger.info(f"Split into {len(chunks)} chunks for VRAM safety.")

        for i, chunk in enumerate(chunks):
            logger.info(f"Analyzing chunk {i+1}/{len(chunks)}...")
            result = self.brain.generate_note(chunk)
            
            if "error" in result:
                logger.error(f"Error processing chunk: {result['error']}")
                continue

            content = result['content']
            
            # Extract title from the content
            title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
            
            if title_match and title_match.group(1).strip() != "{{Title}}":
                title = title_match.group(1).strip()
                # Sanitize title for filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_').lower()
                filename = f"{safe_title}_part_{i+1}.md" if len(chunks) > 1 else f"{safe_title}.md"
            else:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                safe_base = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_').lower()
                filename = f"{safe_base}_part_{i+1}.md" if len(chunks) > 1 else f"{safe_base}.md"

            # Check if file already exists to avoid overwriting
            original_filename = filename
            counter = 1
            while (VAULT_DIR / filename).exists():
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1

            # Save to Obsidian
            with open(VAULT_DIR / filename, "w", encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved chunk {i+1} to Vault as {filename}.")
            
        end_time = time.time()
        logger.info(f"Document processing completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    # Ensure directories exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = ResearchHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    logger.info(f"Research Desk Active. Drop files in: {INBOX_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Research Desk...")
        observer.stop()
    observer.join()