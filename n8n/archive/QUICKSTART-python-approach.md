# n8n RAG Workflow - Quick Start Guide

Get your CV-RAG pipeline running in **30 minutes**.

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ Python 3.11+ installed
- ✅ n8n instance running at `https://flow.imurph.com`
- ✅ Neon Postgres database created
- ✅ Ollama running on VPS with `llama3.2:latest` model
- ✅ This repository cloned locally

## Step-by-Step Setup

### 1. Install Dependencies (5 minutes)

```bash
cd /Users/mikemurphy/Code/Projects/cv-rag

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

**Expected output**: All packages installed successfully, including `flask==3.0.0`

### 2. Configure Environment Variables (3 minutes)

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required values:**
```bash
NEON_CONNECTION_STRING=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query
OLLAMA_API_URL=http://your-vps-ip:11434
```

### 3. Set Up Database (5 minutes)

```bash
# In Neon Console (https://console.neon.tech/):
# 1. Select your project
# 2. Go to SQL Editor
# 3. Copy and paste the contents of docs/setup_database.sql
# 4. Click "Run" to execute

# Verify the table was created
# Run this query in Neon SQL Editor:
SELECT COUNT(*) FROM cv_chunks;
# Expected: 0 (table exists but empty)
```

### 4. Process Documents and Generate Embeddings (5 minutes)

```bash
# Chunk the documents
python scripts/chunker.py
# Expected: ~25-30 chunks created in data/chunks.json

# Generate embeddings and insert into database
python scripts/embedder.py
# Expected: "Successfully inserted X chunks into database"

# Verify embeddings in Neon Console:
# SELECT COUNT(*) FROM cv_chunks;
# Expected: ~25-30 rows
```

### 5. Start Embedding Service (2 minutes)

**Open a NEW terminal window** and run:

```bash
cd /Users/mikemurphy/Code/Projects/cv-rag
source .venv/bin/activate
python scripts/embedding_service.py
```

**Expected output:**
```
Loading sentence-transformers model: all-MiniLM-L6-v2
Model loaded successfully. Embedding dimension: 384
Starting CV-RAG Embedding Service on http://0.0.0.0:8000
```

**Test it** (in another terminal):
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "model": "all-MiniLM-L6-v2", "dimension": 384}
```

**Keep this terminal running** - the service must stay active for n8n to work.

### 6. Import n8n Workflow (5 minutes)

1. **Open n8n**: Navigate to `https://flow.imurph.com`

2. **Import workflow**:
   - Click **Workflows** → **Add workflow** → **Import from File**
   - Select `n8n/cv-rag-workflow.json`
   - Click **Import**

3. **Configure Postgres credentials**:
   - Click on the **Postgres Vector Search** node
   - Click **Create New Credential**
   - Enter your Neon database details:
     - **Host**: Extract from your connection string (e.g., `ep-xxx-xxx.us-east-2.aws.neon.tech`)
     - **Database**: Your database name
     - **User**: Your username
     - **Password**: Your password
     - **Port**: `5432`
     - **SSL**: ✅ Enable (required for Neon)
   - Click **Save**

4. **Update Ollama URL**:
   - Click on the **Ollama - Generate Answer** node
   - In the URL field, replace with your actual VPS IP:
     ```
     http://YOUR_VPS_IP:11434/api/generate
     ```
   - Click **Save** (or just close the node)

5. **Activate workflow**:
   - Toggle the **Inactive** switch to **Active** in the top-right
   - The workflow is now live!

6. **Copy webhook URL**:
   - Click on the **Webhook - Receive Query** node
   - Copy the **Production URL** (should be `https://flow.imurph.com/webhook/cv-rag-query`)
   - Update your `.env` file with this URL if different

### 7. Test the Complete Pipeline (5 minutes)

**Test 1: Quick webhook test**
```bash
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What programming languages does Mike know?"}'
```

**Expected response** (within 5-10 seconds):
```json
{
  "answer": "Based on the resume context, Mike has experience with...",
  "query": "What programming languages does Mike know?",
  "chunks_used": 3,
  "model": "llama3.2:latest",
  "timestamp": "2025-11-03T..."
}
```

**Test 2: Run comprehensive test suite**
```bash
python scripts/test_workflow.py
```

**Expected output:**
```
=== Testing Embedding Service ===
✓ Embedding service is healthy
✓ Embedding generation working (384 dimensions)

=== Testing n8n RAG Workflow ===
✓ Query successful (5/5 passed)

=== Test Summary ===
Passed: 5/5
✓ All tests passed! Your RAG pipeline is working.
```

### 8. Launch Streamlit Frontend (2 minutes)

**Open a THIRD terminal window**:

```bash
cd /Users/mikemurphy/Code/Projects/cv-rag
source .venv/bin/activate
streamlit run streamlit/app.py
```

**Expected**: Browser opens to `http://localhost:8501` with your CV-RAG chat interface.

**Try the sample questions** in the sidebar!

---

## What You Should Have Running

At this point, you should have **3 terminal windows** running:

1. **Terminal 1**: Embedding service (`python scripts/embedding_service.py`)
2. **Terminal 2**: Streamlit app (`streamlit run streamlit/app.py`)
3. **Terminal 3**: Free for testing/debugging

Plus:
- **n8n workflow**: Active at `https://flow.imurph.com`
- **Ollama**: Running on your VPS
- **Neon Postgres**: Cloud database with embeddings

---

## Troubleshooting

### Embedding Service Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Fix**:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### n8n Workflow Fails on Postgres Node

**Error**: `password authentication failed`

**Fix**:
1. Verify connection string in `.env`
2. Check Neon credentials in n8n (Credentials → Postgres)
3. Ensure SSL is enabled in the credential settings
4. Check if Neon database is suspended (free tier auto-suspends after inactivity)

### Ollama Timeout

**Error**: `Request timeout after 60000ms`

**Fix**:
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Check Ollama status
systemctl status ollama

# If not running, start it
systemctl start ollama

# Test from VPS
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.2:latest", "prompt": "test", "stream": false}'

# Check firewall
sudo ufw status
# Ensure port 11434 is open
```

### n8n Workflow Returns 404

**Error**: `404 Not Found`

**Fix**:
1. Check workflow is **Active** (toggle in top-right)
2. Verify webhook URL in `.env` matches the n8n webhook node URL
3. Check n8n execution logs for errors

### No Chunks Retrieved (chunks_used: 0)

**Error**: Response contains `"chunks_used": 0`

**Fix**:
```bash
# Check if embeddings exist in database
# Run in Neon SQL Editor:
SELECT COUNT(*) FROM cv_chunks;

# If 0, run embedder:
python scripts/embedder.py
```

### Test Script Shows Errors

**Fix**:
1. Ensure embedding service is running (`curl http://localhost:8000/health`)
2. Check `.env` has correct `N8N_WEBHOOK_URL`
3. Verify n8n workflow is active
4. Check Ollama is accessible from n8n

---

## Next Steps

Once everything is working:

1. ✅ **Test thoroughly**: Try all sample questions in Streamlit
2. ✅ **Monitor logs**: Watch n8n execution logs for errors
3. ✅ **Optimize**: Adjust Ollama temperature/max_tokens for better responses
4. ✅ **Deploy**: Host Streamlit on Streamlit Cloud or VPS
5. ✅ **Document**: Record demo video for job applications

---

## Production Deployment Checklist

Before going to production:

- [ ] Set up systemd service for embedding service (auto-restart)
- [ ] Add rate limiting to n8n webhook
- [ ] Set up monitoring/alerting for service health
- [ ] Configure backup strategy for Neon database
- [ ] Add HTTPS/authentication to embedding service if exposing externally
- [ ] Set up analytics tracking for queries
- [ ] Test load/performance with concurrent requests
- [ ] Document error handling and recovery procedures

---

## Support Resources

- **Project docs**: `CLAUDE.md` - Comprehensive project documentation
- **n8n setup**: `n8n/README.md` - Detailed workflow documentation
- **Ollama setup**: `docs/OLLAMA_SETUP.md` - VPS installation guide
- **Database schema**: `docs/setup_database.sql` - Database setup SQL

**Need help?** Check the troubleshooting section in `n8n/README.md` for detailed debugging steps.

---

**Congratulations!** 🎉 Your CV-RAG pipeline is now fully operational.
