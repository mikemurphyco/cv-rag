# CV-RAG Quick Start Guide

Get your AI-powered resume running in under 30 minutes!

> **Note:** This project uses n8n workflows for all RAG operations. No Python scripts needed for chunking or embedding!

## Prerequisites

- [x] Python 3.11+ installed
- [x] Neon Postgres account ([console.neon.tech](https://console.neon.tech))
- [x] Hostinger VPS with Ollama installed (see `docs/OLLAMA_SETUP.md`)
- [x] n8n installed on VPS (or use n8n cloud)

## Step 1: Clone & Setup Environment (5 min)

```bash
# Navigate to project
cd cv-rag

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables (5 min)

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

Fill in these required values:
```bash
NEON_CONNECTION_STRING=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/cv-rag-query
OLLAMA_API_URL=http://your-vps-ip:11434
```

## Step 3: Set Up Database (3 min)

1. Log into Neon Console: https://console.neon.tech/
2. Open SQL Editor for your project
3. Copy & paste contents of `docs/setup_database.sql`
4. Execute the SQL

Verify:
```bash
# You should see pgvector enabled and cv_chunks table created
```

## Step 4: Import n8n Workflows (5 min)

1. **Open n8n** at your instance URL (e.g., `https://flow.imurph.com`)

2. **Import Workflow 1 (Document Ingestion):**
   - Click "Workflows" → "Add workflow" → "Import from File"
   - Select: `n8n/workflow-1-document-ingestion.json`
   - Configure Postgres credentials
   - Update Ollama base URL to your VPS IP
   - Activate the workflow

3. **Import Workflow 2 (Query Pipeline):**
   - Click "Workflows" → "Add workflow" → "Import from File"
   - Select: `n8n/workflow-2-query-pipeline.json`
   - Configure Postgres credentials
   - Update Ollama base URLs
   - Activate the workflow

4. **Trigger document ingestion:**
   ```bash
   curl -X POST https://your-n8n.com/webhook/ingest-resume \
     -H "Content-Type: application/json" \
     -d '{"file_path": "/path/to/docs/cv_mike-murphy.md"}'
   ```

**For detailed n8n setup:** See [n8n/README.md](n8n/README.md)

## Step 5: Configure Environment Variables (2 min)

Update your `.env` file with the n8n webhook URL from Workflow 2:

```bash
# Get webhook URL from n8n Workflow 2
# Click the Webhook node → Copy Production URL

N8N_WEBHOOK_URL=https://your-n8n.com/webhook/cv-rag-query
```

## Step 6: Test the Pipeline (3 min)

Test the n8n workflow directly:

```bash
curl -X POST https://your-n8n.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What AI tutorials has Mike created?"}'
```

Expected response:
```json
{
  "answer": "Based on the resume, Mike has created...",
  "query": "What AI tutorials has Mike created?",
  "chunks_used": 3,
  "model": "llama3.2:latest"
}
```

## Step 7: Launch Streamlit App (2 min)

```bash
# Run the Streamlit app
streamlit run streamlit/app.py

# Opens in browser at http://localhost:8501
```

Try the sample questions in the sidebar!

## Verification Checklist

- [ ] Database has ~25-30 chunks with embeddings
- [ ] Direct queries return relevant chunks (similarity > 0.5)
- [ ] n8n webhook responds with LLM-generated answers
- [ ] Streamlit app loads and shows sample questions
- [ ] Sample question "What AI tutorials has Mike created?" returns accurate answer
- [ ] Download buttons work (if PDFs exist)

## Troubleshooting

### n8n workflow import fails
- Ensure you have the latest n8n version with AI nodes
- Update: `docker pull n8nio/n8n:latest` or `npm update -g n8n`
- Look for "Embeddings Ollama" and "Ollama Chat Model" nodes

### "Model not found" error
- Verify Ollama models are installed: `ollama list`
- Pull missing models: `ollama pull nomic-embed-text && ollama pull llama3.2:latest`

### n8n workflow returns empty
- Verify Ollama is running: `curl http://your-vps-ip:11434/api/tags`
- Check Postgres credentials in n8n are correct
- Ensure pgvector extension is enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
- Verify documents were ingested (check Workflow 1 execution logs)

### Streamlit won't start
- Check `N8N_WEBHOOK_URL` is set in `.env`
- Verify n8n workflow is active
- Check port 8501 isn't in use: `lsof -i :8501`

## Next Steps

1. **Customize Prompts**: Edit the Code nodes in Workflow 2 to adjust LLM behavior
2. **Add More Documents**: Trigger Workflow 1 with additional markdown files
3. **Record Demo Video**: Use Streamlit interface to show off your RAG system
4. **Deploy Streamlit**: Push to Streamlit Cloud (free tier available)
5. **Create Tutorial**: Turn this into YouTube content!

## Quick Commands Reference

```bash
# Reactivate environment
source .venv/bin/activate

# Test n8n query workflow
curl -X POST https://your-n8n.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "test question"}'

# Reingest documents after updates
curl -X POST https://your-n8n.com/webhook/ingest-resume \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/updated-resume.md"}'

# Run Streamlit
streamlit run streamlit/app.py

# Check Ollama on VPS
ssh root@your-vps-ip "curl http://localhost:11434/api/tags"

# Test Ollama models
bash scripts/test_ollama_models.sh

# Clean database (resets all chunks)
python scripts/clean_database.py
```

---

**Need more help?**
- **Detailed setup:** [n8n/README.md](n8n/README.md)
- **Complete docs:** [CLAUDE.md](CLAUDE.md)
- **Portfolio overview:** [README.md](README.md)
