# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CV-RAG is an interactive Retrieval-Augmented Generation (RAG) system for Mike Murphy's resume and supplemental materials. The system creates a searchable, chat-based interface where users can query details about skills, experience, tutorials, and more through semantic search and LLM-powered responses.

**Purpose**: Demonstrates AI expertise while serving as a unique job application tool.

## Tech Stack

- **Data Storage**: Neon Postgres with pgvector extension for vector embeddings
- **Embedding Model**: Ollama `nomic-embed-text` (optimized for embeddings, running on VPS)
- **LLM**: Ollama `llama3.2:latest` running on Hostinger VPS KVM2 (8GB RAM, 2 vCPU)
- **Workflow Automation**: n8n with AI/LangChain nodes (complete RAG system built in n8n)
- **Text Processing**: n8n Recursive Character Text Splitter node (500 char chunks, 50 char overlap)
- **Frontend**: Streamlit with custom CSS and sample question buttons
- **Development**: n8n-native workflows (minimal Python), Streamlit for UI
- **Infrastructure**: Self-hosted on Hostinger VPS (n8n + Ollama), Neon Postgres (cloud), Streamlit Cloud/VPS

## Architecture

### RAG Pipeline Flow

**Two n8n Workflows:**

**Workflow 1: Document Ingestion (One-Time Setup)**
1. n8n webhook receives document path
2. Read File node loads markdown
3. Recursive Text Splitter node chunks text (500 chars, 50 overlap)
4. Embeddings Ollama node converts chunks to vectors (nomic-embed-text)
5. Postgres Vector Store node inserts into Neon database

**Workflow 2: Query Pipeline (Runtime)**
1. User query → n8n webhook trigger
2. Embeddings Ollama node converts query to vector
3. Postgres Vector Store node retrieves top 3 similar chunks
4. Format Context node builds LLM prompt with retrieved chunks
5. Ollama Chat Model node generates answer (llama3.2:latest)
6. Response returned to Streamlit frontend

### Key Components

**scripts/**
- ~~`chunker.py`~~: (Deprecated - now handled by n8n Text Splitter node)
- ~~`embedder.py`~~: (Deprecated - now handled by n8n Embeddings Ollama node)
- ~~`embedding_service.py`~~: (Deprecated - n8n calls Ollama directly)
- `test_workflow.py`: Test suite for the n8n RAG pipeline

**streamlit/**
- `app.py`: Chat interface with sample questions and resume download link

**docs/**
- `cv_mike-murphy.md`: Main resume content
- `supplemental.md`: Additional info (YouTube tutorials, courses, skills stories)
- `cover-letter_template.md`: Cover letter template

**n8n/**
- `workflow-1-document-ingestion.json`: n8n workflow for ingesting and chunking documents
- `workflow-2-query-pipeline.json`: n8n workflow for handling user queries
- `N8N_NATIVE_SETUP.md`: **START HERE** - Complete setup guide for n8n-native RAG system
- `README.md`: Legacy documentation (older Python-based approach)
- `QUICKSTART.md`: Legacy quick start guide
- `ARCHITECTURE.md`: Legacy architecture documentation

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Actual Dependencies (from requirements.txt)
- `langchain==0.3.7` - Text splitting utilities
- `langchain-text-splitters==0.3.2` - RecursiveCharacterTextSplitter
- `sentence-transformers==3.3.1` - all-MiniLM-L6-v2 embedding model
- `psycopg2-binary==2.9.10` - PostgreSQL database adapter
- `pgvector==0.3.6` - Vector similarity operations
- `python-dotenv==1.0.1` - Environment variable management
- `requests==2.32.3` - HTTP requests to n8n webhooks
- `streamlit==1.40.2` - Web UI framework
- `pandas==2.2.3` - Data handling utilities
- `flask==3.0.0` - Embedding service HTTP server

### Database Setup
```sql
-- Enable pgvector extension in Neon Postgres
CREATE EXTENSION vector;

-- Create documents table (adjust dimension for your embedder)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(384)
);
```

### Environment Variables
Create a `.env` file (not committed) with:
- `NEON_CONNECTION_STRING`: Postgres connection string
- `OLLAMA_API_URL`: VPS Ollama endpoint (e.g., http://your-vps-ip:11434)
- `N8N_WEBHOOK_URL`: n8n query webhook endpoint

## Running the Application

### Process Documents
```bash
# Chunk documents into segments
python scripts/chunker.py

# Generate embeddings and store in database
python scripts/embedder.py
```

### Test Queries
```bash
# Test query workflow
python scripts/query.py
```

### Run Streamlit Frontend
```bash
streamlit run streamlit/app.py
```

### Ollama on VPS (Docker)
```bash
# Run Ollama container
docker run -d -p 11434:11434 --name ollama ollama/ollama

# Pull Llama 3 model
docker exec ollama ollama pull llama3.2:latest

# Test API
curl http://your-vps-ip:11434/api/generate \
  -d '{"model": "llama3", "prompt": "Hello"}'
```

## Development Phases

The project follows a 5-phase roadmap (see sandbox/roadmap.md):
1. **Project Setup**: Environment, Git, folder structure
2. **Data Preparation**: Chunk and process documents
3. **RAG Implementation**: Database, embeddings, n8n workflow, Ollama integration
4. **Frontend**: Streamlit chat interface
5. **Polish & Deployment**: Error handling, testing, deployment

**Current status**: Phase 2/3 complete - All scripts implemented, ready for database setup and n8n workflow configuration

## Implementation Details

### Chunking (scripts/chunker.py)
- Uses `RecursiveCharacterTextSplitter` with 500 char chunks, 50 char overlap
- Separators: `["\n\n", "\n", ". ", " "]` (preserves semantic boundaries)
- Processes `docs/cv_mike-murphy.md` and `docs/supplemental.md`
- Outputs to `data/chunks.json` with metadata (source, chunk_index, total_chunks)
- Expected output: ~25-30 chunks total

### Embedding (scripts/embedder.py)
- Model: `all-MiniLM-L6-v2` (384-dimensional vectors)
- Batch encoding for efficiency (shows progress bar)
- Creates `cv_chunks` table with pgvector extension
- Vector index: `ivfflat` with cosine similarity (`vector_cosine_ops`)
- Index parameter: `lists = 10` (optimized for <100 chunks)

### Database Schema (docs/setup_database.sql)
```sql
CREATE TABLE cv_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,  -- 'resume' or 'supplemental'
    chunk_index INTEGER,
    total_chunks INTEGER,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Query Testing (scripts/query.py)
- **Direct mode**: Tests vector search without LLM (for debugging)
- **n8n mode**: Tests full RAG pipeline with Ollama
- **Interactive mode**: Manual query testing
- Returns top 3 chunks by cosine similarity

### Streamlit App (streamlit/app.py)
- 6 pre-configured sample questions for demo video
- Sidebar with tech stack explanation
- Download buttons for resume PDF and cover letter
- Error handling for missing webhook configuration
- Footer with social links and tech attribution

### n8n Workflow Configuration
**Required nodes:**
1. Webhook (POST) - Receives query
2. Embedding Service - Generates query embedding (use HTTP Request to local model or OpenAI API)
3. Postgres Vector Search - Finds top 3 similar chunks
4. Context Formatter - Combines chunks into prompt context
5. Ollama Node - Generates answer with llama3.2:latest
6. Respond to Webhook - Returns JSON with 'answer' field

**Critical SQL query for node 3:**
```sql
SELECT content, source,
       1 - (embedding <=> $1::vector) AS similarity
FROM cv_chunks
ORDER BY embedding <=> $1::vector
LIMIT 3;
```

## Important Notes

- **Security**: `.env` file is gitignored - never commit secrets
- **Data Privacy**: Resume content is public, but connection strings are secret
- **Chunking Strategy**: 500 chars balances context vs. precision for small resume corpus
- **Vector Dimension**: Must match across embedding model (384), Postgres schema, and n8n
- **n8n Workflow**: Can be exported to `n8n/cv-rag-workflow.json` for version control (remove sensitive data first)
- **Ollama Setup**: See `docs/OLLAMA_SETUP.md` for VPS installation with external access configuration
- **Quick Start**: See `QUICKSTART.md` for 30-minute setup guide

## Files Reference

- `QUICKSTART.md` - Step-by-step setup (start here!)
- `docs/OLLAMA_SETUP.md` - VPS installation guide with firewall config
- `docs/setup_database.sql` - Copy-paste database schema for Neon console
- `.env.example` - Template for environment variables
- `requirements.txt` - Pinned dependency versions
- `.gitignore` - Protects secrets and generated data files

## Next Steps After Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Set up database: Run `docs/setup_database.sql` in Neon console
4. Process documents: `python scripts/chunker.py && python scripts/embedder.py`
5. Install Ollama on VPS: Follow `docs/OLLAMA_SETUP.md`
6. Build n8n workflow (see Implementation Details above)
7. Test pipeline: `python scripts/query.py`
8. Launch Streamlit: `streamlit run streamlit/app.py`
9. Record demo video for job applications
10. Deploy to Streamlit Cloud and update README with live link

## Troubleshooting Common Issues

**Import Error: `langchain_text_splitters`**
- Ensure `langchain-text-splitters==0.3.2` is installed
- Activate virtual environment first

**Database Connection Fails**
- Verify Neon connection string includes `?sslmode=require`
- Check database isn't suspended (free tier limitation)

**Ollama Timeout**
- Verify Ollama is running: `ssh root@vps "systemctl status ollama"`
- Test external access: `curl http://vps-ip:11434`
- Check firewall: `sudo ufw status`

**Streamlit 404 on Webhook**
- Ensure n8n workflow is active (not paused)
- Verify `N8N_WEBHOOK_URL` in `.env` matches n8n webhook node URL
- Test webhook directly: `curl -X POST <webhook-url> -d '{"query":"test"}'`

## Future Enhancements

- Tutorial series documenting the build process
- PDF export of resume from Markdown
- Analytics dashboard for query patterns
- Multi-language support
- Voice interface using Whisper + ElevenLabs
- Product: "AI Resume Chat" SaaS for other job seekers
