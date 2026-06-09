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

1. **Clone or navigate to the project directory**:
   ```bash
   cd langchain-llm
   ```

2. **Create a Python virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to match your setup (usually defaults are fine if Ollama is running locally).

## Usage

### First Run

```bash
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
# Rebuild the vector store to include new files
python src/app.py --rebuild
```

Without `--rebuild`, the system uses the cached vector database. Use `--rebuild` when you add, remove, or significantly update wiki files.

## Configuration

Edit `.env` to customize behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKI_DIR` | `./wiki` | Path to your markdown wiki files |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model to use |
| `LLM_MODEL` | `llama3` | LLM model for generating answers |

Example `.env`:
```env
WIKI_DIR=./wiki
OLLAMA_BASE_URL=http://localhost:11434
EMBED_MODEL=nomic-embed-text
LLM_MODEL=llama3
```

## Project Structure

```
langchain-llm/
├── src/
│   ├── __init__.py           # Package marker
│   ├── loader.py             # Load and chunk markdown files
│   ├── vectorstore.py        # Build/load Chroma vector store
│   ├── chain.py              # RAG chain assembly
│   └── app.py                # CLI entry point
├── wiki/
│   └── sample.md             # Example wiki file (add your own)
├── .chroma/                  # Vector database (auto-created)
├── requirements.txt          # Python dependencies
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

**chain.py**:
- Creates a `ChatOllama` instance for answer generation
- Defines a system prompt for context-aware responses
- Assembles LCEL chain: retriever → formatter → prompt → LLM → output parser

**app.py**:
- Orchestrates vectorstore initialization
- Runs the interactive question-answer loop
- Handles `--rebuild` flag for reindexing

## How RAG Works

1. **Retrieval**: Your question is converted to an embedding and compared against stored document embeddings
2. **Ranking**: The top 3 most similar document chunks are retrieved
3. **Augmentation**: Retrieved chunks are inserted into the LLM prompt as context
4. **Generation**: The LLM generates an answer based on your question + provided context

This approach ensures answers are grounded in your actual wiki content.

## Troubleshooting

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

**Error**: `llama3 not found` or similar

**Solution**:
```bash
# Pull the required models
ollama pull llama3
ollama pull nomic-embed-text

# Verify they're installed
ollama list
```

### Vector database errors

**Error**: Chroma-related errors

**Solution**: Delete `.chroma/` directory and rebuild:
```bash
rm -rf .chroma
python src/app.py
```

The vector database will be rebuilt from scratch.

### Poor answer quality

- **Add more wiki content**: The system can only answer based on what's in your wiki
- **Improve wiki structure**: Clear, well-organized sections work better than walls of text
- **Adjust temperature**: Edit `src/chain.py` to change `temperature` parameter (lower = more focused, higher = more creative)
- **Try different models**: You can swap `LLM_MODEL` in `.env` (e.g., try `llama2` or other Ollama models)

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

Change `LLM_MODEL` in `.env`:
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
- Requires Ollama to be running (can't use OpenAI, Anthropic, etc. without modifying code)
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
