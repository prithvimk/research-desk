# Research Desk: Project Context & Architecture

This document serves as a comprehensive guide for any AI model or developer trying to understand the `research-desk` project.

## 1. Project Overview

**Research Desk** is an automated, AI-powered knowledge management system. It acts as an autonomous agent that monitors an "Inbox" for raw text/documents, uses a local Large Language Model (LLM) to synthesize that text into structured Obsidian notes, and automatically archives them into an Obsidian Vault. Additionally, it has a built-in mechanism to generate weekly executive summary newsletters by analyzing the Git commit history of the Obsidian Vault.

The project relies entirely on local models (e.g., IBM Granite or Google Gemma) served via `llama.cpp` or Ollama, ensuring 100% privacy and local execution.

---

## 2. Directory Structure

```text
research-desk/
├── .env                        # Core environment variables (paths, LLM endpoints)
├── start_brain.bat             # Batch script to boot the llama.cpp server with model params
├── requirements.txt            # Python dependencies (watchdog, requests, PyYAML, etc.)
├── data/
│   ├── 01_inbox/               # Watched folder where raw text files are dropped
│   ├── 02_processed/           # (Reserved) For files that have been successfully parsed
│   ├── 03_vector_store/        # (Reserved) Potential RAG/embeddings storage
│   └── 04_obsidian_vault/      # The Git-tracked Obsidian Vault where output notes are saved
├── prompts/                    # YAML files defining prompts and model parameters
│   ├── note_synthesis.yaml     # Prompt and parameters for creating Obsidian notes
│   └── weekly_newsletter.yaml  # Prompt and parameters for generating the weekly delta
└── src/                        # Core Python application logic
    ├── brain.py                # LLM API client wrapper
    ├── watcher.py              # Watchdog service that monitors the Inbox
    ├── newsletter.py           # Weekly summary generator based on Git history
    ├── config.py               # Central configuration module (loads from .env)
    ├── logger.py               # Central logging module
    └── prompt_manager.py       # Helper to load and parse YAML prompt configurations
```

---

## 3. Core Components

### A. `src/watcher.py` (The Intake Engine)
- **Role**: Uses the `watchdog` library to monitor the `data/01_inbox` directory continuously.
- **Workflow**:
  1. Detects a new `.txt` or `.md` file.
  2. Reads the file and uses `langchain_text_splitters.RecursiveCharacterTextSplitter` to chunk the text into VRAM-safe sizes (e.g., 3000 tokens).
  3. Sends each chunk sequentially to `ResearchBrain`.
  4. Parses the LLM's response to extract the generated title.
  5. Saves the output directly into `data/04_obsidian_vault/` using a sanitized, intuitive filename (appending `_part_x` if the document was split into multiple chunks).

### B. `src/brain.py` (The LLM Interface)
- **Role**: The core communication bridge between the Python application and the local LLM server.
- **Workflow**:
  1. `process_chunk(text, prompt_config)`: Takes user content and a prompt configuration dictionary (containing system instructions, `temperature`, and `top_k`).
  2. Constructs an OpenAI-spec compatible payload.
  3. Issues a raw HTTP POST request using `requests` to the local API endpoint defined in `.env` (typically `http://127.0.0.1:8080/v1/chat/completions` or port `11434`).
  4. Returns the synthesized markdown content.

### C. `src/newsletter.py` (The Synthesizer)
- **Role**: Generates a weekly executive summary of all new knowledge added to the vault.
- **Workflow**:
  1. Opens the `data/04_obsidian_vault` directory as a Git repository using `gitpython`.
  2. Iterates over all commits from the last 7 days to identify modified or newly added `.md` files.
  3. Concatenates the contents of these changed files into a massive "Weekly Delta" string.
  4. Sends the delta to `ResearchBrain` using the `weekly_newsletter.yaml` prompt configuration.
  5. Saves the output to `data/04_obsidian_vault/Newsletter/Weekly_Brief_YYYY-WXX.md`.

### D. `src/prompt_manager.py` (Configuration Loader)
- **Role**: A utility module that abstracts prompt loading.
- **Workflow**: Reads `.yaml` files from the `prompts/` directory using `PyYAML`. It maps the YAML into a Python dictionary, allowing `brain.py` to dynamically apply context-specific `temperature` and `top_k` settings to different inference tasks.

### E. `start_brain.bat` (The Server Bootstrapper)
- **Role**: A Windows batch script that boots the local LLM server using `llama-server.exe`.
- **Workflow**: It is currently configured to load `granite-4.0-h-tiny-Q4_K_M` as the main model and `granite-4.0-1b-Q4_K_M` as a draft model (utilizing speculative decoding for faster inference speeds). It binds to port `8080`.

---

## 4. Configuration Pipeline

The application relies strictly on environment variables for configuration to prevent hardcoded parameters:
1. `.env` defines the variables (`LLM_API_URL`, `LLM_MODEL_NAME`, chunk sizes, etc.).
2. `src/config.py` loads `.env` using `python-dotenv` and exports these values as Python constants, normalizing directory paths using `pathlib.Path`.
3. The rest of the application imports from `src/config.py`.

---

## 5. Development Guidelines & Rules

- **Logging**: Do not use `print()`. Always import `get_logger` from `src/logger.py` and use `logger.info()`, `logger.error()`, etc.
- **Prompt Modification**: Never hardcode system prompts or LLM hyper-parameters in the `.py` files. Create or modify `.yaml` files inside the `prompts/` directory.
- **Paths**: Never use relative string paths like `"./data/..."`. Always use the `pathlib.Path` objects exported by `src/config.py` (e.g., `VAULT_DIR / filename`).
