# LangChain RAG System with Local Wiki

A retrieval-augmented generation (RAG) system that connects your local markdown wiki with a local LLM (Ollama) using LangChain. Ask questions about your wiki content and get accurate answers grounded in your knowledge base.

## Features

- **Local-first**: Run everything locally with no API keys or internet required
- **Semantic search**: Uses embeddings to find relevant wiki sections
- **Persistent storage**: Vector database caches embeddings for fast startup
- **Easy wiki management**: Drop markdown files into the `wiki/` directory
- **Interactive CLI**: Simple question-and-answer interface
- **Configurable**: All settings available via `.env`

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **Ollama** installed and running
   - Download from [ollama.ai](https://ollama.ai)
   - Start the Ollama service on your machine
3. **Required Ollama models**:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

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
   Edit `.env` to match your setup (usually defaults are fine if Ollama is running locally).

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
1. Load all markdown files from your `wiki/` directory
2. Split them into chunks
3. Generate embeddings using `nomic-embed-text`
4. Build and persist a vector database in `.chroma/`

Then it enters interactive mode.

### Asking Questions

```
Ask a question: What is LangChain?
Searching...

Answer: LangChain is a framework for developing applications powered by language models...
```

Type `exit` to quit the program.

### Adding Wiki Files

Simply add `.md` files to the `wiki/` directory, then:

```bash
source venv/bin/activate
python src/app.py --rebuild
```

Without `--rebuild`, the system uses the cached vector database. Use `--rebuild` when you add, remove, or significantly update wiki files.

## Configuration

Copy `.env.example` to `.env` and edit as needed. See `.env.example` for all options (Ollama, Hugging Face, OpenAI, Cursor).

Common variables for the default Ollama setup:

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKI_DIR` | `./wiki` | Path to your markdown wiki files |
| `LLM_PROVIDER` | `ollama` | LLM backend (`ollama`, `huggingface`, `openai`, `cursor`) |
| `EMBED_PROVIDER` | `ollama` | Embedding backend (`ollama`, `huggingface`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `OLLAMA_LLM_MODEL` | `llama3` | LLM model for generating answers |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model to use |

Legacy aliases `LLM_MODEL` and `EMBED_MODEL` still work and map to the Ollama settings above.

Example `.env`:
```env
WIKI_DIR=./wiki
LLM_PROVIDER=ollama
EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Project Structure

```
langchain-llm/
├── src/
│   ├── config.py             # Load settings from .env
│   ├── providers/            # LLM & embedding factory (Ollama, HF, etc.)
│   ├── loader.py             # Load and chunk markdown files
│   ├── vectorstore.py        # Build/load Chroma vector store
│   ├── chain.py              # RAG chain assembly
│   └── app.py                # CLI entry point
├── venv/                     # Python virtual environment (local, gitignored)
├── wiki/
│   └── sample.md             # Example wiki file (add your own)
├── .chroma/                  # Vector database (auto-created)
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
[chain.py] - Build RAG chain
    ↓
[app.py] - Interactive loop
```

### Component Details

**loader.py**:
- Recursively loads all `.md` files from `wiki/`
- Splits documents into chunks (500 chars, 50 char overlap)
- Returns list of `Document` objects

**vectorstore.py**:
- Uses `OllamaEmbeddings` to convert text to vectors
- Persists vectors in `.chroma/` directory
- Loads cached vectorstore on startup (unless `--rebuild`)

**providers/**:
- `llm_factory.py` / `embeddings_factory.py` create models from `LLM_PROVIDER` / `EMBED_PROVIDER`
- Supports Ollama (default), Hugging Face, OpenAI, and Cursor Agent API

**chain.py**:
- Accepts any LangChain `BaseChatModel` from the factory
- Defines a system prompt for context-aware responses
- Assembles LCEL chain: retriever → formatter → prompt → LLM → output parser

**app.py**:
- Loads settings, builds embeddings and LLM via factories
- Runs the interactive question-answer loop
- Handles `--rebuild` flag for reindexing

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

**Error**: `Connection refused` or `Connection error`

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

**Error**: `model "nomic-embed-text" not found` or similar

**Cause**: RAG needs **two** Ollama models — an LLM for answers and a separate embedding model for search. Having only `qwen3.6:27b` (or `llama3`) is not enough.

**Solution**:
```bash
# Pull both models configured in .env
ollama pull nomic-embed-text    # embedding (OLLAMA_EMBED_MODEL)
ollama pull qwen3.6:27b         # LLM (OLLAMA_LLM_MODEL) — if not already installed

# Verify they're installed
ollama list

# Rebuild vectorstore after embedding model is available
source venv/bin/activate
python src/app.py --rebuild
```

### Vector database errors

**Error**: Chroma-related errors

**Solution**: Delete `.chroma/` directory and rebuild:
```bash
source venv/bin/activate
rm -rf .chroma
python src/app.py
```

The vector database will be rebuilt from scratch.

### Poor answer quality

- **Add more wiki content**: The system can only answer based on what's in your wiki
- **Improve wiki structure**: Clear, well-organized sections work better than walls of text
- **Adjust temperature**: Edit `src/chain.py` to change `temperature` parameter (lower = more focused, higher = more creative)
- **Try different models**: Change `OLLAMA_LLM_MODEL` in `.env` (e.g., try `llama2` or other Ollama models)

## Performance Tips

- **First run is slow**: Embedding generation takes time. Subsequent runs use cached vectors
- **Chunk size matters**: Smaller chunks = better relevance but more API calls. Edit `src/loader.py` if needed
- **k parameter**: Currently retrieves top 3 documents. Adjust in `src/app.py` (get_retriever call) for more/fewer results

## Example Wiki Content

The project includes `wiki/sample.md` as an example. You can:

1. Replace it with your own markdown files
2. Add multiple files to the directory
3. Use any markdown format (headers, lists, code blocks, etc.)

Example structure:
```markdown
# My Knowledge Base

## Topic 1
Content here...

## Topic 2
- Point 1
- Point 2

## Code Examples
```python
# Your code
```
```

All content will be indexed and searchable.

## Development

### Running Tests

To verify everything is set up correctly:
```bash
source venv/bin/activate

# Ensure Ollama models are available
ollama list

# Start the app (models will be loaded on first question)
python src/app.py

# Ask a test question about content in wiki/sample.md
# Example: "What is LangChain?"
```

### Modifying the System Prompt

Edit the `prompt` variable in `src/chain.py` to customize the LLM's behavior:
```python
prompt = PromptTemplate(
    template="""Your custom instructions here...
    
Context: {context}
Question: {question}
Answer:""",
    input_variables=["context", "question"],
)
```

### Using Different Ollama Models

Change `OLLAMA_LLM_MODEL` in `.env`:
- `llama2`: Smaller, faster
- `neural-chat`: Good for conversation
- `mistral`: Fast and capable
- `dolphin-mixtral`: Larger, more capable

Make sure the model is pulled:
```bash
ollama pull [model-name]
```

## What's Happening Under the Hood

When you ask a question:

1. Your question is embedded using `nomic-embed-text`
2. Semantic similarity is calculated against all stored document chunks
3. Top 3 most similar chunks are retrieved
4. A prompt is constructed: `[system instruction] + [retrieved chunks] + [your question]`
5. The prompt is sent to `llama3` running via Ollama
6. The answer is streamed and printed

## Limitations

- Answers are limited to content in your wiki
- Default setup requires Ollama to be running; cloud providers need API keys in `.env`
- Changing the embedding provider requires rebuilding the vector store (`--rebuild`)
- Vector database is not distributed (local only)
- No user authentication or multi-user support

## Future Enhancements

- Support for source attribution (showing which wiki file was used)
- Web UI instead of CLI
- Multi-document answer summarization
- Support for non-markdown file formats
- Streaming responses for long answers
- Feedback/relevance scoring

## License

This project is provided as-is for your personal use.

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Verify Ollama is running and models are installed
3. Check `.env` configuration matches your setup
4. Review wiki file formatting (should be standard markdown)

---

**Happy learning with your local RAG system!** 🚀
