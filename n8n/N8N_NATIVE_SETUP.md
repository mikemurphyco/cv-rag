# n8n-Native RAG System Setup Guide

This guide shows you how to build a **complete RAG system using n8n's built-in AI nodes**. This showcases your n8n skills by doing everything inside n8n workflows!

## Why This Approach is Better for Your Portfolio

**Original approach:** Python scripts do the work, n8n just calls them
- ❌ Doesn't showcase your n8n skills
- ❌ Looks like you're just wrapping Python code
- ❌ Harder to explain in interviews

**New n8n-native approach:** Everything built with n8n nodes
- ✅ Shows you understand n8n AI/LangChain nodes
- ✅ Demonstrates workflow design skills
- ✅ Easy to show in demos and interviews
- ✅ Still uses your VPS Ollama + Neon setup

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    TWO N8N WORKFLOWS                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  WORKFLOW 1: Document Ingestion (one-time setup)                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  Webhook → Read File → Extract Text →                     │  │
│  │  Recursive Text Splitter → Embeddings Ollama →            │  │
│  │  Postgres Vector Store (Insert)                           │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  WORKFLOW 2: Query Pipeline (runtime)                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  Webhook → Embeddings Ollama → Postgres Vector Store      │  │
│  │  (Retrieve) → Format Context → Ollama Chat Model →        │  │
│  │  Respond                                                   │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                           │
                           │ Uses
                           ▼
        ┌──────────────────────────────────────────┐
        │  Your Infrastructure                     │
        │  • Ollama (VPS) - nomic-embed-text       │
        │  • Ollama (VPS) - llama3.2:latest        │
        │  • Neon Postgres - pgvector              │
        └──────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Ollama on VPS with Required Models

You need **two models** installed on your Ollama VPS:

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Pull the embedding model (smaller, faster)
ollama pull nomic-embed-text

# You already have the chat model
ollama list
# Should show: llama3.2:latest

# Test both models
ollama run nomic-embed-text "test"
ollama run llama3.2:latest "test"
```

**Why nomic-embed-text?**
- Specifically designed for embeddings (not chat)
- Smaller than using llama3.2 for embeddings
- Faster embedding generation
- Industry standard for Ollama-based RAG

### 2. Neon Postgres Database

Your database needs the pgvector extension enabled:

```sql
-- Run in Neon SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it's enabled
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Note:** You DON'T need to create the `cv_chunks` table manually. The n8n Vector Store node will create it automatically!

### 3. n8n Instance

Your n8n at `https://flow.imurph.com` needs to be updated to support AI nodes.

**Check if you have AI nodes:**
- Open n8n
- Click to add a new node
- Search for "Embeddings Ollama"
- If you see it, you're good! ✅
- If not, you need to update n8n

**To update n8n:**
```bash
# SSH into your VPS where n8n is running
ssh root@your-vps-ip

# If using Docker:
docker pull n8nio/n8n:latest
docker restart n8n

# If using npm:
npm update -g n8n
```

---

## Setup Steps

### Step 1: Import Both Workflows

1. **Open n8n** at `https://flow.imurph.com`

2. **Import Workflow 1 (Document Ingestion)**
   - Workflows → Add workflow → Import from File
   - Select: `n8n/workflow-1-document-ingestion.json`
   - Click Import

3. **Import Workflow 2 (Query Pipeline)**
   - Workflows → Add workflow → Import from File
   - Select: `n8n/workflow-2-query-pipeline.json`
   - Click Import

### Step 2: Configure Credentials (Both Workflows)

Both workflows need the same credentials:

**A. Postgres Credentials**
1. Click on any **Postgres Vector Store** node
2. Click **Create New Credential**
3. Enter your Neon details:
   - **Host**: `your-project.neon.tech`
   - **Database**: `your-database-name`
   - **User**: `your-username`
   - **Password**: `your-password`
   - **Port**: `5432`
   - **SSL**: ✅ Enable
4. Click **Save**

**B. Set Environment Variables** (Optional but recommended)
- n8n Settings → Variables
- Add: `OLLAMA_API_URL` = `http://your-vps-ip:11434`

Or hardcode your VPS IP in each Ollama node.

### Step 3: Configure Ollama Nodes

In **both workflows**, update Ollama nodes with your VPS URL:

**Workflow 1 - Embeddings Ollama node:**
- Model: `nomic-embed-text`
- Base URL: `http://your-vps-ip:11434`

**Workflow 2 - Two Ollama nodes:**
- **Embeddings Ollama**:
  - Model: `nomic-embed-text`
  - Base URL: `http://your-vps-ip:11434`
- **Ollama Chat Model**:
  - Model: `llama3.2:latest`
  - Base URL: `http://your-vps-ip:11434`

### Step 4: Test Workflow 1 (Document Ingestion)

1. **Activate Workflow 1**
   - Toggle **Inactive** → **Active**

2. **Get the webhook URL**
   - Click on the **Webhook - Trigger Ingestion** node
   - Copy the Production URL (e.g., `https://flow.imurph.com/webhook/ingest-resume`)

3. **Prepare your resume file**
   - Make sure `docs/cv_mike-murphy.md` exists in your project
   - Copy it to your VPS or make it accessible to n8n

4. **Trigger the workflow**
   ```bash
   curl -X POST https://flow.imurph.com/webhook/ingest-resume \
     -H "Content-Type: application/json" \
     -d '{
       "file_path": "/path/to/your/docs/cv_mike-murphy.md"
     }'
   ```

5. **Expected response:**
   ```json
   {
     "success": true,
     "message": "Successfully ingested resume",
     "chunks_created": 25,
     "embedding_model": "nomic-embed-text",
     "vector_store": "Neon Postgres (pgvector)",
     "timestamp": "2025-11-03T..."
   }
   ```

6. **Verify in Neon Console:**
   ```sql
   SELECT COUNT(*) FROM cv_chunks;
   -- Should return: ~25-30 rows

   SELECT chunk_id, LEFT(content, 50) as preview
   FROM cv_chunks
   LIMIT 5;
   ```

### Step 5: Test Workflow 2 (Query Pipeline)

1. **Activate Workflow 2**
   - Toggle **Inactive** → **Active**

2. **Get the webhook URL**
   - Click on the **Webhook - Receive Query** node
   - Copy the Production URL (e.g., `https://flow.imurph.com/webhook/cv-rag-query`)

3. **Test with a query**
   ```bash
   curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What programming languages does Mike know?"
     }'
   ```

4. **Expected response:**
   ```json
   {
     "answer": "Based on the resume context, Mike has experience with...",
     "query": "What programming languages does Mike know?",
     "chunks_used": 3,
     "model": "llama3.2:latest",
     "embedding_model": "nomic-embed-text",
     "timestamp": "2025-11-03T..."
   }
   ```

### Step 6: Connect Streamlit Frontend

1. **Update your `.env` file:**
   ```bash
   N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query
   ```

2. **Run Streamlit:**
   ```bash
   streamlit run streamlit/app.py
   ```

3. **Test the UI:**
   - Try the sample questions
   - The answers should come from your n8n workflow!

---

## What Each n8n Node Does

### Workflow 1: Document Ingestion

| Node | Type | Purpose |
|------|------|---------|
| **Webhook - Trigger Ingestion** | Webhook | Receives file path to ingest |
| **Read Resume File** | Read Binary File | Reads markdown file from disk |
| **Extract Text from File** | Extract from File | Converts binary to text |
| **Recursive Text Splitter** | LangChain Text Splitter | Splits text into 500-char chunks with 50 overlap |
| **Embeddings Ollama** | LangChain Embeddings | Converts chunks to vectors using nomic-embed-text |
| **Postgres Vector Store - Insert** | LangChain Vector Store | Stores chunks + embeddings in Neon |
| **Format Response** | Code | Creates success message JSON |
| **Respond to Webhook** | Respond to Webhook | Returns result to caller |

### Workflow 2: Query Pipeline

| Node | Type | Purpose |
|------|------|---------|
| **Webhook - Receive Query** | Webhook | Receives user question |
| **Embeddings Ollama - Query** | LangChain Embeddings | Converts question to vector |
| **Postgres Vector Store - Retrieve** | LangChain Vector Store | Finds top 3 similar chunks |
| **Format Context** | Code | Combines chunks into LLM prompt |
| **Ollama Chat Model** | LangChain Chat Model | Generates answer using llama3.2:latest |
| **Format Final Response** | Code | Structures JSON response |
| **Respond to Webhook** | Respond to Webhook | Returns answer to Streamlit |

---

## Advantages of This Approach

### For Your Portfolio

✅ **Shows n8n expertise**: Using AI/LangChain nodes, not just HTTP requests
✅ **RAG implementation**: Real-world AI workflow design
✅ **Vector database integration**: pgvector with Postgres
✅ **Self-hosted LLM**: Ollama on your own VPS
✅ **Production-ready**: Two-workflow separation (ingestion vs. query)

### For Interviews

You can confidently say:
- "I built a RAG system entirely in n8n using LangChain nodes"
- "I configured Ollama embeddings and chat models on my VPS"
- "I integrated pgvector for semantic search in Postgres"
- "I designed separate workflows for data ingestion and querying"

### Technical Benefits

- **No Python dependencies**: Everything runs in n8n
- **Visual workflow**: Easy to debug and modify
- **Scalable**: Can add more documents by triggering Workflow 1
- **Maintainable**: Clear separation of concerns

---

## Troubleshooting

### "Embeddings Ollama node not found"

**Problem**: Your n8n version is too old

**Solution**:
```bash
# Update n8n
docker pull n8nio/n8n:latest  # if using Docker
npm update -g n8n  # if using npm
```

### "Model nomic-embed-text not found"

**Problem**: Model not installed on Ollama

**Solution**:
```bash
ssh root@your-vps-ip
ollama pull nomic-embed-text
ollama list  # verify it's installed
```

### "Postgres Vector Store node fails"

**Problem**: pgvector extension not enabled

**Solution**:
```sql
-- Run in Neon Console
CREATE EXTENSION IF NOT EXISTS vector;
```

### "Chunks not being inserted"

**Problem**: Table configuration issue

**Solution**: Delete the table and let n8n recreate it:
```sql
DROP TABLE IF EXISTS cv_chunks;
```
Then re-run Workflow 1.

### "Ollama timeout"

**Problem**: VPS Ollama not accessible

**Solution**:
```bash
# Test from your local machine
curl http://your-vps-ip:11434/api/tags

# Check firewall
ssh root@your-vps-ip
sudo ufw status
sudo ufw allow 11434
```

---

## Next Steps

1. ✅ Import both workflows into n8n
2. ✅ Configure credentials (Postgres)
3. ✅ Update Ollama base URLs
4. ✅ Run Workflow 1 to ingest your resume
5. ✅ Test Workflow 2 with sample queries
6. ✅ Connect Streamlit frontend
7. 📝 Add more documents (supplemental.md, cover letter, etc.)
8. 📝 Customize prompts for better answers
9. 📝 Add analytics/logging
10. 📝 Deploy Streamlit to production

---

## Comparison: Old vs New Approach

| Aspect | Python Scripts | n8n-Native |
|--------|----------------|------------|
| **Chunking** | `chunker.py` script | Recursive Text Splitter node |
| **Embeddings** | `embedder.py` + `embedding_service.py` | Embeddings Ollama node |
| **Vector Store** | Python psycopg2 | Postgres Vector Store node |
| **Query** | Python requests → n8n | Direct n8n workflow |
| **Portfolio Value** | Shows Python skills | Shows n8n skills ✅ |
| **Maintenance** | Multiple scripts | Single n8n instance |
| **Visibility** | Code in files | Visual workflows |

---

**Ready to build your n8n-native RAG system? Start with Step 1!** 🚀
