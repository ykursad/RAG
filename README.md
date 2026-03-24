# Single Document RAG UI

A modern web application for document-based question answering using Retrieval-Augmented Generation (RAG) with local AI models.

## Features

- **Document Ingestion**: Upload and process PDF/txt documents
- **Intelligent Chunking**: Smart text splitting with overlap for better context retention
- **Vector Search**: Fast similarity search using ChromaDB
- **Local AI**: Uses Ollama for embeddings and chat models (no API keys required)
- **Web Interface**: Clean, responsive UI for document upload and Q&A
- **REST API**: FastAPI backend with comprehensive endpoints
- **Logging**: Detailed logging for debugging and monitoring

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Vector DB**: ChromaDB
- **AI Models**: Ollama (Gemma models)
- **Embeddings**: Local embedding models via Ollama
- **Deployment**: Uvicorn

## Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running
3. **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ykursad/single-doc-rag-ui.git
   cd single-doc-rag-ui
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama models**
   ```bash
   # Pull the required models
   ollama pull gemma3:4b          # Chat model
   ollama pull embeddinggemma     # Embedding model
   ```

4. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start the application**
   ```bash
   # Make sure Ollama is running first
   ollama serve

   # Start the app
   python -m uvicorn app.main:app --reload
   ```

6. **Open your browser**
   ```
   http://localhost:8000
   ```

## Usage

1. **Upload a document** using the web interface
2. **Ask questions** about the document content
3. **Get AI-powered answers** with source citations

## API Endpoints

- `GET /` - Web interface
- `POST /ingest` - Upload and process documents
- `POST /ask` - Ask questions
- `POST /retrieve` - Retrieve relevant chunks only
- `GET /health` - Health check
- `POST /reset` - Reset the index

## Configuration

Key settings in `app/config.py`:

- `ollama_base_url`: Ollama server URL
- `ollama_chat_model`: Chat model name
- `ollama_embed_model`: Embedding model name
- `chunk_size`: Text chunk size
- `chunk_overlap`: Chunk overlap for context
- `top_k`: Number of chunks to retrieve

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Project Structure

```
single_doc_rag_ui/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── rag_service.py     # Main RAG logic
│   │   ├── ollama_client.py   # Ollama integration
│   │   ├── vector_store.py    # ChromaDB wrapper
│   │   ├── chunker.py         # Text chunking
│   │   └── document_loader.py # Document processing
│   ├── static/                # CSS/JS assets
│   ├── templates/             # HTML templates
│   ├── config.py              # Configuration
│   ├── schemas.py             # Pydantic models
│   └── main.py                # FastAPI app
├── data/                     # Vector DB and uploads
├── tests/                    # Unit tests
└── requirements.txt          # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Ollama](https://ollama.ai/)
- Vector search with [ChromaDB](https://www.trychroma.com/)