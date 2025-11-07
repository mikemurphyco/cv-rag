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
- `test_workflow.py`: Test suite for the n8n RAG pipeline
- `clean_database.py`: Utility to reset database during development
- `test_ollama_models.sh`: Tests Ollama model availability
- `check_ollama_status.sh`: Checks Ollama service status

**archive/** (deprecated files for reference)
- `archive/scripts/`: Old Python-based chunking/embedding scripts
- `archive/*.md`: Development notes and deployment experiments

**streamlit/**
- `app.py`: Chat interface with sample questions and resume download link

**docs/**
- `cv_mike-murphy.md`: Main resume content
- `supplemental.md`: Additional info (YouTube tutorials, courses, skills stories)
- `cover-letter_template.md`: Cover letter template

**n8n/**
- `README.md`: **START HERE** - Complete setup guide for n8n-native RAG system
- `workflow-1-document-ingestion.json`: n8n workflow for ingesting and chunking documents
- `workflow-2-query-pipeline.json`: n8n workflow for handling user queries
- `archive/`: Deprecated Python-based approach documentation (kept for reference)

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
- `streamlit==1.40.2` - Web UI framework
- `requests==2.32.3` - HTTP requests to n8n webhooks
- `python-dotenv==1.0.1` - Environment variable management
- `pandas==2.2.3` - Data handling utilities (for Streamlit)

**Deprecated (for old Python-based approach):**
- `langchain==0.3.7` - No longer needed (n8n has built-in nodes)
- `sentence-transformers==3.3.1` - Replaced by Ollama nomic-embed-text
- `psycopg2-binary==2.9.10` - No longer needed (n8n handles database)
- `pgvector==0.3.6` - No longer needed (n8n handles vectors)
- `flask==3.0.0` - No longer needed (n8n calls Ollama directly)

### Database Setup
```sql
-- Enable pgvector extension in Neon Postgres
CREATE EXTENSION IF NOT EXISTS vector;

-- Table is automatically created by n8n Postgres Vector Store node
-- No manual table creation needed!
```

### Environment Variables
Create a `.env` file (not committed) with:
- `NEON_CONNECTION_STRING`: Postgres connection string
- `OLLAMA_API_URL`: VPS Ollama endpoint (e.g., http://your-vps-ip:11434)
- `N8N_WEBHOOK_URL`: n8n query webhook endpoint

## Running the Application (n8n-Native Approach)

### 1. Set up Ollama on VPS
```bash
# Pull required models
ssh root@your-vps-ip
ollama pull nomic-embed-text  # For embeddings
ollama pull llama3.2:latest   # For chat

# Verify models
ollama list
```

### 2. Import n8n Workflows
1. Open n8n at `https://flow.imurph.com`
2. Import `n8n/workflow-1-document-ingestion.json`
3. Import `n8n/workflow-2-query-pipeline.json`
4. Configure Postgres credentials in both workflows
5. Update Ollama base URLs to your VPS IP
6. Activate both workflows

### 3. Ingest Documents
```bash
# Trigger workflow 1 to process your resume
curl -X POST https://flow.imurph.com/webhook/ingest-resume \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/docs/cv_mike-murphy.md"}'
```

### 4. Run Streamlit Frontend
```bash
streamlit run streamlit/app.py
```

### 5. Test the Pipeline
```bash
# Query your resume
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Mikes skills?"}'
```

**See `n8n/README.md` for complete setup instructions.**

## Development Phases

The project follows a 5-phase roadmap (see sandbox/roadmap.md):
1. **Project Setup**: Environment, Git, folder structure
2. **Data Preparation**: Chunk and process documents
3. **RAG Implementation**: Database, embeddings, n8n workflow, Ollama integration
4. **Frontend**: Streamlit chat interface
5. **Polish & Deployment**: Error handling, testing, deployment

**Current status**: Phase 3 - n8n workflows created, ready for import and testing

## Implementation Details (n8n-Native Approach)

### Workflow 1: Document Ingestion
**Handled entirely by n8n nodes:**
1. **Webhook** - Receives document path
2. **Read File** - Loads markdown content
3. **Recursive Text Splitter** - Chunks text (500 chars, 50 overlap)
4. **Embeddings Ollama** - Generates vectors using `nomic-embed-text`
5. **Postgres Vector Store** - Inserts into Neon database

**No Python scripts needed!** All chunking and embedding happens in n8n.

### Workflow 2: Query Pipeline
**Complete RAG pipeline in n8n:**
1. **Webhook** - Receives user query
2. **Embeddings Ollama** - Converts query to vector
3. **Postgres Vector Store** - Retrieves top 3 similar chunks
4. **Code Node** - Formats context for LLM
5. **Ollama Chat Model** - Generates answer using `llama3.2:latest`
6. **Respond to Webhook** - Returns JSON response

### Database
**Auto-created by n8n:**
- Table: `cv_chunks` (created automatically by Postgres Vector Store node)
- Embeddings: 768-dimensional vectors (nomic-embed-text default)
- Index: Automatically managed by n8n

### Embedding Model
- **Model**: Ollama `nomic-embed-text` (optimized for RAG)
- **Dimension**: 768 (default for nomic-embed-text)
- **Location**: Self-hosted on VPS
- **No local embedding service needed** - n8n calls Ollama directly

### Streamlit App (streamlit/app.py)
- 6 pre-configured sample questions for demo video
- Sidebar with tech stack explanation
- Download buttons for resume PDF and cover letter
- Error handling for missing webhook configuration
- Footer with social links and tech attribution

### n8n Workflow Nodes (Already Configured in JSON Files)
**Workflow 1 (Ingestion):**
1. Webhook - Trigger ingestion
2. Read Binary File - Load markdown
3. Extract from File - Convert to text
4. Recursive Text Splitter - Chunk text (n8n LangChain node)
5. Embeddings Ollama - Generate vectors (n8n AI node)
6. Postgres Vector Store - Insert chunks (n8n LangChain node)

**Workflow 2 (Query):**
1. Webhook - Receive query
2. Embeddings Ollama - Convert query to vector (n8n AI node)
3. Postgres Vector Store - Retrieve similar chunks (n8n LangChain node)
4. Code - Format context
5. Ollama Chat Model - Generate answer (n8n AI node)
6. Respond to Webhook - Return JSON

**No manual SQL needed** - the Postgres Vector Store node handles all vector operations!

## Production Deployment (VPS)

**Mike's production environment runs on Hostinger VPS with 3 Docker Compose projects:**

### Architecture Overview
```
app-net (shared Docker network)
├── n8n + Traefik (flow.imurph.com) - n8n workflows with SSL termination
├── Ollama (internal only) - LLM + embedding models
└── cv-rag-streamlit (chat.imurph.com) - Streamlit frontend with SSL
```

### Docker Compose Projects

**1. n8n** (at `/root/n8n/docker-compose.yml`)
- Traefik reverse proxy (ports 80/443, SSL with Let's Encrypt)
- n8n workflow engine at `https://flow.imurph.com`
- Both services connected to `app-net` network

**2. Ollama** (at `/root/ollama/docker-compose.yml`)
- Ollama container (internal only, no public ports)
- Models: `nomic-embed-text`, `llama3.2:latest`
- Connected to `app-net` network
- Accessible by n8n at `http://ollama:11434`

**3. cv-rag** (at `/root/cv-rag/docker-compose.yml`)
- Streamlit container at `https://chat.imurph.com`
- Uses Traefik labels for SSL termination
- Connects to n8n webhooks for RAG queries
- Mounts `./docs` and `./streamlit/app.py` as read-only volumes

### Updating Production

**When pulling repo updates to VPS:**
```bash
# Preserve production docker-compose.yml (it's deployment-specific)
cd /root/cv-rag
cp docker-compose.yml docker-compose.yml.production
cp .env .env.production

# Pull updates
git stash
git pull origin main

# Restore production configs
cp docker-compose.yml.production docker-compose.yml
cp .env.production .env

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

**Why docker-compose.yml is not in repo:**
- Contains deployment-specific Traefik labels and network configuration
- Each deployment (VPS vs Streamlit Cloud) has different infrastructure needs
- VPS version is preserved locally and not version controlled

## Important Notes

- **Security**: `.env` file is gitignored - never commit secrets
- **Data Privacy**: Resume content is public, but connection strings are secret
- **Chunking Strategy**: 500 chars balances context vs. precision for small resume corpus
- **Vector Dimension**: 768 (nomic-embed-text default) - automatically handled by n8n
- **n8n Workflows**: Two separate workflows for ingestion and querying
- **Ollama Models**: Both `nomic-embed-text` and `llama3.2:latest` must be installed on VPS
- **Setup Guide**: See `n8n/README.md` for complete n8n-native setup instructions
- **Production URLs**:
  - n8n: https://flow.imurph.com
  - Streamlit: https://chat.imurph.com
  - Ollama: Internal only (http://ollama:11434 from n8n)

## Files Reference

**Core Files:**
- `README.md` - Main portfolio README (start here for overview)
- `QUICKSTART.md` - Quick setup guide for getting the system running
- `CLAUDE.md` - This file - detailed project documentation for AI assistants
- `.env.example` - Template for environment variables
- `requirements.txt` - Minimal dependencies (mostly Streamlit)

**n8n Workflows:**
- `n8n/README.md` - **Detailed n8n setup guide**
- `n8n/workflow-1-document-ingestion.json` - Document ingestion workflow
- `n8n/workflow-2-query-pipeline.json` - Query handling workflow (production version)
- `n8n/archive/` - Older workflow versions for reference

**Scripts & Testing:**
- `scripts/test_workflow.py` - End-to-end workflow testing
- `scripts/clean_database.py` - Database reset utility
- `scripts/test_ollama_models.sh` - Ollama model tests
- `scripts/check_ollama_status.sh` - Ollama service status

**Archive:**
- `archive/` - Deprecated files kept for reference (old Python scripts, deployment experiments)

## Next Steps After Setup

**Follow the guide in `n8n/README.md` for complete setup. Quick overview:**

1. Pull Ollama models on VPS: `ollama pull nomic-embed-text` and `ollama pull llama3.2:latest`
2. Import both n8n workflows from `n8n/` directory
3. Configure Postgres credentials in n8n
4. Update Ollama base URLs in workflow nodes
5. Activate both workflows
6. Test ingestion workflow with your resume
7. Test query workflow with sample questions
8. Configure `.env` with n8n webhook URL
9. Launch Streamlit: `streamlit run streamlit/app.py`
10. Record demo video and deploy to production

## Troubleshooting Common Issues

**n8n Workflow Fails - "Model not found"**
- Ensure both Ollama models are installed: `ollama list` on VPS
- Pull missing models: `ollama pull nomic-embed-text` and `ollama pull llama3.2:latest`

**n8n Workflow Fails - Postgres Connection**
- Verify Neon credentials in n8n are correct
- Check SSL is enabled in Postgres credential settings
- Ensure pgvector extension is enabled: `CREATE EXTENSION IF NOT EXISTS vector;`

**Ollama Timeout in n8n**
- Verify Ollama is running on VPS: `ssh root@vps "curl http://localhost:11434/api/tags"`
- Check firewall allows port 11434: `sudo ufw allow 11434`
- Update base URL in n8n Ollama nodes to match your VPS IP

**Streamlit Can't Connect to n8n**
- Ensure both n8n workflows are active (not paused)
- Verify `N8N_WEBHOOK_URL` in `.env` matches workflow 2 webhook URL
- Test webhook directly: `curl -X POST <webhook-url> -H "Content-Type: application/json" -d '{"query":"test"}'`

**No AI Nodes in n8n**
- Update n8n to latest version: `docker pull n8nio/n8n:latest` or `npm update -g n8n`
- Look for "Embeddings Ollama" and "Ollama Chat Model" nodes

## Future Enhancements

- Tutorial series documenting the build process
- PDF export of resume from Markdown
- Analytics dashboard for query patterns
- Multi-language support
- Voice interface using Whisper + ElevenLabs
- Product: "AI Resume Chat" SaaS for other job seekers
