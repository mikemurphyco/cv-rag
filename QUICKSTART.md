# CV-RAG Quick Start Guide

Get your AI-powered resume running in under 30 minutes!

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

## Step 4: Process Your Resume (5 min)

```bash
# Step 1: Chunk the documents
python scripts/chunker.py

# Expected output:
# ✅ Created ~25-30 chunks
# 📁 Saved to: data/chunks.json

# Step 2: Generate embeddings and store in database
python scripts/embedder.py

# Expected output:
# ✅ Generated embeddings with dimension 384
# ✅ All chunks inserted successfully
# 📊 Database contains X chunks
```

## Step 5: Set Up n8n Workflow (10 min)

### Option A: Import JSON (Fastest)

1. Copy the workflow from `n8n/cv-rag-workflow.json` (you'll need to create this)
2. In n8n, click "Import from File"
3. Update these nodes:
   - **Webhook**: Note the webhook URL
   - **Postgres**: Add your Neon connection string
   - **Ollama**: Set base URL to `http://your-vps-ip:11434`

### Option B: Build Manually

Create a workflow with these nodes:

```
1. Webhook (POST)
   └─> 2. Code (Extract query from body)
       └─> 3. Embeddings (Generate query embedding)
           └─> 4. Postgres (Vector similarity search)
               └─> 5. Code (Format context)
                   └─> 6. Ollama (Generate answer)
                       └─> 7. Respond to Webhook
```

**Detailed node configurations:**

**Node 1: Webhook**
- Method: POST
- Path: `cv-rag-query`
- Response Mode: "Last Node"

**Node 3: Embeddings** (use HTTP Request to local sentence-transformers or OpenAI)
- Endpoint: Your embedding service
- Model: `all-MiniLM-L6-v2`

**Node 4: Postgres**
```sql
SELECT
    content,
    source,
    1 - (embedding <=> '{{ $json.embedding }}'::vector) AS similarity
FROM cv_chunks
ORDER BY embedding <=> '{{ $json.embedding }}'::vector
LIMIT 3;
```

**Node 6: Ollama**
- Base URL: `http://your-vps-ip:11434`
- Model: `llama3.2:latest`
- Prompt template:
```
You are an AI assistant answering questions about Mike Murphy's resume and experience.

Context from Mike's resume:
{{ $json.context }}

Question: {{ $json.query }}

Provide a helpful, accurate answer based on the context above.
```

**Save and activate the workflow!**

Update your `.env` with the webhook URL.

## Step 6: Test the Pipeline (5 min)

```bash
# Run the query tester
python scripts/query.py

# Choose option 1 (Direct database query) first
# Try: "What AI tutorials has Mike created?"

# Then try option 2 (Full n8n pipeline)
# This tests the complete RAG system with LLM
```

Expected behavior:
- Direct query shows relevant resume chunks with similarity scores
- n8n query returns a natural language answer from Ollama

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

### Chunker fails
- Check that `docs/cv_mike-murphy.md` and `docs/supplemental.md` exist
- Ensure virtual environment is activated

### Embedder fails with connection error
- Verify `NEON_CONNECTION_STRING` in `.env` is correct
- Test connection: `psql "your-connection-string"`
- Check Neon database is running (free tier doesn't auto-sleep)

### n8n workflow returns empty
- Verify Ollama is running: `curl http://your-vps-ip:11434`
- Check Postgres query returns results in n8n's "Execute Node" test
- Review n8n execution logs for errors

### Streamlit won't start
- Check `N8N_WEBHOOK_URL` is set in `.env`
- Verify n8n workflow is active
- Check port 8501 isn't in use: `lsof -i :8501`

## Next Steps

1. **Record Demo Video**: Use Streamlit interface to show off your RAG system
2. **Deploy Streamlit**: Push to Streamlit Cloud or host on VPS
3. **Update README**: Add screenshots and demo link
4. **Create Tutorial**: Turn this into YouTube content!

## Quick Commands Reference

```bash
# Reactivate environment
source .venv/bin/activate

# Re-chunk after resume updates
python scripts/chunker.py && python scripts/embedder.py

# Test queries
python scripts/query.py

# Run Streamlit
streamlit run streamlit/app.py

# Check Ollama on VPS
ssh root@your-vps-ip "systemctl status ollama"
```

---

**Need help?** Check `CLAUDE.md` for detailed architecture info or `docs/OLLAMA_SETUP.md` for VPS setup.
