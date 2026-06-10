# LangChain RAG System with Local Wiki

A retrieval-augmented generation (RAG) system that connects your local markdown wiki with an LLM using LangChain. Ask questions about your wiki content and get answers grounded in your knowledge base.

## Features

- **Local-first**: Default Ollama setup runs locally with no API keys required
- **Multi-provider**: Swap LLM/embedding backends — Ollama, Hugging Face, OpenAI, or Cursor
- **Korean support**: Korean response prompts and multilingual embedding defaults (`bge-m3`)
- **Semantic search**: Uses embeddings to find relevant wiki sections
- **Persistent storage**: Vector database caches embeddings for fast startup
- **Auto-reindex**: Rebuilds the vectorstore when the embedding model changes
- **Easy wiki management**: Point `WIKI_DIR` at any directory of `.md` files
- **Interactive CLI**: Simple question-and-answer interface
- **Configurable**: All settings available via `.env` and `.env.local`

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **Ollama** installed and running
   - Download from [ollama.ai](https://ollama.ai)
   - Start the Ollama service on your machine
3. **Required Ollama models** (default setup uses two different models):

   | Role | Variable | Default model | Purpose |
   |------|----------|---------------|---------|
   | Chat (LLM) | `OLLAMA_LLM_MODEL` | `qwen2.5:7b` | Generates answers |
   | Embedding | `OLLAMA_EMBED_MODEL` | `bge-m3` | Semantic search |

   ```bash
   ollama pull qwen2.5:7b    # LLM — answer generation
   ollama pull bge-m3        # Embedding — retrieval
   ```

   Chat and embedding models are **not interchangeable**. Do not put `bge-m3` in `OLLAMA_LLM_MODEL`.

## Installation

This project uses a **Python virtual environment (`venv`)**. Install dependencies inside `venv` so they stay isolated from your system Python (required on macOS with Homebrew Python).

1. **Clone or navigate to the project directory**:
   ```bash
   cd langchain-llm
   ```

2. **Create and activate the virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS / Linux
   # venv\Scripts\activate    # Windows (PowerShell / cmd)
   ```

   Your shell prompt should show `(venv)`. Run all commands below with the venv active.

3. **Install dependencies** (inside the activated venv):
   ```bash
   # Default Ollama setup (smaller install)
   pip install -r requirements-ollama.txt

   # Or install optional Hugging Face / Cursor providers too:
   # pip install -r requirements-extra.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to match your setup. **`WIKI_DIR` must be set to the path of your own markdown wiki** — the value in `.env.example` (`./wiki`) is only a placeholder. Use an absolute or relative path to wherever your `.md` files live.

   For personal overrides without touching `.env`, create `.env.local` (loaded with higher priority).

### Cursor / VS Code

Point the editor at the venv interpreter so the integrated terminal and Run/Debug use the same environment:

- **Interpreter**: `./venv/bin/python` (macOS / Linux) or `venv\Scripts\python.exe` (Windows)
- Or run **Python: Select Interpreter** and choose the `venv` entry for this project.

You do not need to activate venv manually in the terminal if the correct interpreter is selected.

## Usage

All commands assume the virtual environment is active (`source venv/bin/activate`).

### First Run

```bash
source venv/bin/activate
python src/app.py
```

On first run, the system will:
1. Validate that required Ollama models are installed
2. Load all markdown files from `WIKI_DIR`
3. Split them into chunks
4. Generate embeddings using `OLLAMA_EMBED_MODEL` (default: `bge-m3`)
5. Build and persist a vector database in `.chroma/`
6. Save embedding model metadata to `.chroma/.embed_model`

Then it enters interactive mode. Subsequent runs load the cached vectorstore unless a rebuild is needed.

### Asking Questions

```
Ask a question: 비올라 프로젝트 구조는?
Searching...

Answer: (한국어로 위키 맥락 기반 답변)
```

```
Ask a question: What is LangChain?
Searching...

Answer: LangChain is a framework for developing applications powered by language models...
```

Type `exit` to quit the program.

### Adding Wiki Files

Add or update `.md` files in the directory set by `WIKI_DIR`, then:

```bash
source venv/bin/activate
python src/app.py --rebuild
```

### When to Rebuild

| Situation | Action |
|-----------|--------|
| Wiki files added, removed, or updated | `python src/app.py --rebuild` |
| `OLLAMA_EMBED_MODEL` or `EMBED_PROVIDER` changed | Automatic rebuild on next run |
| `OLLAMA_LLM_MODEL` changed only | No rebuild needed |
| Chroma errors or stale index | `rm -rf .chroma` then `python src/app.py` |

Without `--rebuild`, the system uses the cached vector database.

## Korean Wiki Setup (Recommended)

For Korean wikis and Korean questions, use this combination (`WIKI_DIR` → your wiki path):

```env
WIKI_DIR=/path/to/your/korean-wiki
LLM_PROVIDER=ollama
EMBED_PROVIDER=ollama
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=bge-m3
RESPONSE_LANGUAGE=ko
```

- **`bge-m3`**: Multilingual embeddings — good for Korean retrieval
- **`qwen2.5:7b`**: Lightweight chat model (~5 GB) with solid Korean support
- **`qwen3.6:27b`**: Heavier option if you need higher answer quality (~17 GB)
- **`nomic-embed-text`**: English-focused embedding — not recommended for Korean wikis

There is no `qwen3.6:7b` tag on Ollama. For a lighter Qwen setup, use `qwen2.5:7b` or `qwen2.5:3b`.

## Configuration

Copy `.env.example` to `.env` and edit as needed. See `.env.example` for all options.

> **Note:** `WIKI_DIR` is not shared across users. Each person must set it in their own `.env` (or `.env.local`) to point at their wiki directory. The default `./wiki` is the bundled sample folder; replace it with your actual wiki path before running.

### Ollama (default)

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKI_DIR` | `./wiki` | **User-defined** path to markdown wiki files (you must set this) |
| `PERSIST_DIR` | `.chroma` | Vector database storage path |
| `LLM_PROVIDER` | `ollama` | LLM backend (`ollama`, `huggingface`, `openai`, `cursor`) |
| `EMBED_PROVIDER` | `ollama` | Embedding backend (`ollama`, `huggingface`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `OLLAMA_LLM_MODEL` | `qwen2.5:7b` | Chat model for generating answers |
| `OLLAMA_EMBED_MODEL` | `bge-m3` | Embedding model for retrieval |
| `RESPONSE_LANGUAGE` | `ko` | Answer language (`ko` or `en`) |

Legacy aliases `LLM_MODEL` and `EMBED_MODEL` still work and map to the Ollama settings above.

Example `.env` (set `WIKI_DIR` to your wiki location):
```env
WIKI_DIR=/path/to/your/wiki
LLM_PROVIDER=ollama
EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=bge-m3
RESPONSE_LANGUAGE=ko
```

### Other Providers

| Provider | `LLM_PROVIDER` | Required packages | API key |
|----------|----------------|-------------------|---------|
| Ollama | `ollama` | `requirements-ollama.txt` | None |
| Hugging Face | `huggingface` | `requirements-extra.txt` | `HUGGINGFACEHUB_API_TOKEN` |
| OpenAI | `openai` | `requirements-extra.txt` | `OPENAI_API_KEY` |
| Cursor | `cursor` | `requirements-extra.txt` | `CURSOR_API_KEY` |

Set `HF_LLM_MODEL`, `HF_EMBED_MODEL`, `OPENAI_LLM_MODEL`, or `CURSOR_MODEL` in `.env` as needed. See `.env.example` for all variables.

## Project Structure

```
langchain-llm/
├── src/
│   ├── config.py             # Load settings from .env / .env.local
│   ├── providers/
│   │   ├── llm_factory.py        # Create LLM from provider settings
│   │   ├── embeddings_factory.py # Create embeddings from provider settings
│   │   ├── ollama_health.py      # Validate Ollama models at startup
│   │   └── cursor_adapter.py     # Cursor Agent API adapter
│   ├── loader.py             # Load and chunk markdown files
│   ├── vectorstore.py        # Build/load Chroma vector store
│   ├── chain.py              # RAG chain assembly (Korean/English prompts)
│   └── app.py                # CLI entry point
├── venv/                     # Python virtual environment (local, gitignored)
├── wiki/
│   └── sample.md             # Example wiki file (add your own)
├── .chroma/                  # Vector database (auto-created)
│   └── .embed_model          # Tracks which embedding model built the index
├── requirements-ollama.txt   # Minimal Python dependencies (default)
├── requirements-extra.txt    # Optional HF / Cursor providers
├── requirements.txt          # Points to requirements-ollama.txt
├── .env.example              # Configuration template
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

## Architecture

### Data Flow

```
Wiki Files (.md)
    ↓
[loader.py] - Load & chunk documents
    ↓
[vectorstore.py] - Generate embeddings & store in Chroma
    ↓
[chain.py] - Build RAG chain (language-aware prompt)
    ↓
[app.py] - Interactive loop
```

### Component Details

**loader.py**:
- Recursively loads all `.md` files from `WIKI_DIR`
- Splits documents into chunks (500 chars, 50 char overlap)
- Returns list of `Document` objects

**vectorstore.py**:
- Builds embeddings via the configured provider factory
- Persists vectors in `.chroma/`
- Clears and rebuilds the index when `rebuild=True`

**providers/**:
- `llm_factory.py` / `embeddings_factory.py` create models from `LLM_PROVIDER` / `EMBED_PROVIDER`
- `ollama_health.py` checks Ollama connectivity and model availability before startup
- Supports Ollama (default), Hugging Face, OpenAI, and Cursor Agent API

**chain.py**:
- Selects Korean or English prompt based on `RESPONSE_LANGUAGE`
- Assembles LCEL chain: retriever → formatter → prompt → LLM → output parser

**app.py**:
- Loads settings, validates Ollama models, builds embeddings and LLM via factories
- Auto-rebuilds when embedding model metadata is missing or changed
- Runs the interactive question-answer loop
- Handles `--rebuild` flag for wiki content changes

## How RAG Works

1. **Retrieval**: Your question is converted to an embedding and compared against stored document embeddings
2. **Ranking**: The top 3 most similar document chunks are retrieved
3. **Augmentation**: Retrieved chunks are inserted into the LLM prompt as context
4. **Generation**: The LLM generates an answer based on your question + provided context

This approach ensures answers are grounded in your actual wiki content.

## Troubleshooting

### `No space left on device` during `pip install`

**Error**: `OSError: [Errno 28] No space left on device`

**Cause**: Your disk is full. ML packages (especially `chromadb`) need several hundred MB to install.

**Solution** — free space first, then install the minimal Ollama requirements:

```bash
# 1. Free space (macOS examples)
pip cache purge                    # clears ~/.cache/pip
brew cleanup -s                    # clears old Homebrew downloads (~GB)
# Also: empty Trash, remove large unused files

# 2. Check free space (need at least 1–2 GB recommended)
df -h .

# 3. Install minimal deps only
source venv/bin/activate
pip install -r requirements-ollama.txt
```

Use `requirements-extra.txt` only when you need Hugging Face or Cursor providers.

### `pip install` blocked (externally-managed-environment)

**Error**: `externally-managed-environment` when running `pip install` without venv

**Solution**: Use the project venv instead of system Python:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-ollama.txt
```

### `ModuleNotFoundError` when running the app

**Error**: `No module named 'dotenv'` (or other packages)

**Solution**: Dependencies are installed in `venv`, but the app was run with system Python. Activate venv first:
```bash
source venv/bin/activate
python src/app.py
```

Or run explicitly:
```bash
./venv/bin/python src/app.py
```

### Ollama not responding

**Error**: `Connection refused`, `Connection error`, or `Cannot reach Ollama`

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not running, start Ollama (check Ollama docs for your OS)
# On macOS: Ollama app should be running
# On Linux: systemctl start ollama
# On Windows: Start Ollama from Start menu
```

Verify Ollama is at the URL in your `.env` (default: `http://localhost:11434`).

### Model not found

**Error**: `model "qwen2.5:7b" not found` or `Required Ollama model(s) are not installed`

**Cause**: RAG needs **two** Ollama models — a chat model for answers and a separate embedding model for search.

**Solution**: The app prints the exact `ollama pull` commands on startup. Typically:
```bash
ollama pull qwen2.5:7b    # LLM (OLLAMA_LLM_MODEL)
ollama pull bge-m3        # Embedding (OLLAMA_EMBED_MODEL)

ollama list
python src/app.py --rebuild
```

### `"bge-m3" does not support chat`

**Cause**: An embedding model was set as `OLLAMA_LLM_MODEL`. Embedding models cannot generate chat responses.

**Solution**: Keep roles separate:
```env
OLLAMA_LLM_MODEL=qwen2.5:7b    # chat
OLLAMA_EMBED_MODEL=bge-m3      # embedding
```

### Vector database errors

**Error**: Chroma-related errors or poor retrieval after model change

**Solution**: Delete `.chroma/` and rebuild:
```bash
source venv/bin/activate
rm -rf .chroma
python src/app.py
```

The vector database will be rebuilt from scratch.

### Poor answer quality

- **Add more wiki content**: The system can only answer based on what's in your wiki
- **Improve wiki structure**: Clear, well-organized sections work better than walls of text
- **Use the right embedding model**: For Korean wikis, keep `OLLAMA_EMBED_MODEL=bge-m3`
- **Adjust temperature**: Edit `temperature` in `src/providers/llm_factory.py` (lower = more focused)
- **Try a larger LLM**: Switch `OLLAMA_LLM_MODEL` to `qwen3.6:27b` if `qwen2.5:7b` is too weak

## Performance Tips

- **First run is slow**: Embedding generation takes time. Subsequent runs use cached vectors
- **LLM size matters**: `qwen2.5:7b` is much faster than `qwen3.6:27b` on local hardware
- **Chunk size matters**: Smaller chunks = better relevance but more embedding calls. Edit `src/loader.py` if needed
- **k parameter**: Currently retrieves top 3 documents. Adjust in `src/app.py` (`get_retriever` call) for more/fewer results

## Example Wiki Content

The project includes `wiki/sample.md` as an example. You can:

1. Replace it with your own markdown files
2. Add multiple files to the directory (including nested folders)
3. Use any markdown format (headers, lists, code blocks, etc.)
4. Point `WIKI_DIR` at an external wiki directory

Example structure:
```markdown
# My Knowledge Base

## Topic 1
Content here...

## Topic 2
- Point 1
- Point 2
```

All content will be indexed and searchable.

## Development

### Running Tests

To verify everything is set up correctly:
```bash
source venv/bin/activate

ollama list    # should show qwen2.5:7b and bge-m3

python src/app.py

# Korean wiki example:
# "이 프로젝트의 목적은?"

# English sample wiki example:
# "What is LangChain?"
```

### Modifying the System Prompt

Answer language is controlled by `RESPONSE_LANGUAGE` in `.env` (`ko` or `en`).

To customize prompt text, edit `_prompt_for_language()` in `src/chain.py`.

### Using Different Ollama Models

**Chat models** (`OLLAMA_LLM_MODEL`):
- `qwen2.5:7b` — default, lightweight, good Korean (~5 GB)
- `qwen2.5:3b` — even lighter (~2 GB)
- `qwen3.6:27b` — higher quality, much slower (~17 GB)
- `llama3` — English-leaning alternative

**Embedding models** (`OLLAMA_EMBED_MODEL`):
- `bge-m3` — default, Korean/multilingual retrieval
- `nomic-embed-text` — English-focused, smaller

```bash
ollama pull [model-name]
```

After changing an embedding model, the index rebuilds automatically on next run.

## What's Happening Under the Hood

When you ask a question:

1. Your question is embedded using `OLLAMA_EMBED_MODEL` (e.g. `bge-m3`)
2. Semantic similarity is calculated against all stored document chunks
3. Top 3 most similar chunks are retrieved
4. A prompt is constructed in the configured language (`RESPONSE_LANGUAGE`)
5. The prompt is sent to `OLLAMA_LLM_MODEL` (e.g. `qwen2.5:7b`) via Ollama
6. The answer is printed

## Limitations

- Answers are limited to content in your wiki
- Default setup requires Ollama to be running; cloud providers need API keys in `.env`
- Wiki content changes require `--rebuild`; embedding model changes rebuild automatically
- Vector database is local only (not distributed)
- No user authentication or multi-user support

## License

This project is provided as-is for your personal use.

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Verify Ollama is running and both models are installed (`ollama list`)
3. Check `.env` configuration — especially LLM vs embedding model roles
4. Review wiki file formatting (should be standard markdown)
