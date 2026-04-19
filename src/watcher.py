import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter
from brain import ResearchBrain
from config import INBOX_DIR, VAULT_DIR, CHUNK_SIZE, CHUNK_OVERLAP

class ResearchHandler(FileSystemEventHandler):
    def __init__(self):
        self.brain = ResearchBrain()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".txt") and not event.src_path.endswith(".md"):
            return
        
        print(f"📄 Processing: {os.path.basename(event.src_path)}")
        self.process_file(event.src_path)

    def process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        # Split long papers into GPU-friendly chunks
        chunks = self.splitter.split_text(raw_text)
        print(f"🧩 Split into {len(chunks)} chunks for VRAM safety.")

        for i, chunk in enumerate(chunks):
            print(f"🧠 Analyzing chunk {i+1}/{len(chunks)}...")
            result = self.brain.generate_note(chunk)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue

            # Save to Obsidian
            filename = f"Research_Note_{int(time.time())}_{i}.md"
            with open(VAULT_DIR / filename, "w", encoding='utf-8') as f:
                f.write(result['content'])
            
            print(f"💾 Saved chunk {i+1} to Vault.")

if __name__ == "__main__":
    # Ensure directories exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = ResearchHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    print(f"📡 Research Desk Active. Drop files in: {INBOX_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()