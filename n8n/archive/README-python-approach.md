# n8n RAG Workflow Setup

This directory contains the n8n workflow configuration for the CV-RAG query pipeline.

## Overview

The `cv-rag-workflow.json` file defines a complete Retrieval-Augmented Generation (RAG) pipeline that:

1. Receives user queries via webhook
2. Generates embeddings using sentence-transformers
3. Performs vector similarity search in Neon Postgres
4. Formats context from retrieved chunks
5. Generates LLM responses using Ollama
6. Returns formatted JSON to the Streamlit frontend

## Workflow Architecture

```
User Query (Streamlit)
    ↓
[Webhook] → [Generate Embedding] → [Postgres Vector Search]
    ↓
[Format Context] → [Ollama LLM] → [Format Response] → [Respond to Webhook]
    ↓
Answer (Streamlit)
```

## Prerequisites

### 1. Embedding Service (Local)

You need a local HTTP server that generates embeddings using `all-MiniLM-L6-v2`. Create this service:

**File: `scripts/embedding_service.py`**

```python
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    embedding = model.encode(text)

    # Convert to list for JSON serialization
    embedding_list = embedding.tolist()

    return jsonify({
        'embedding': embedding_list,
        'dimension': len(embedding_list),
        'model': 'all-MiniLM-L6-v2'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**Install dependencies:**
```bash
pip install flask sentence-transformers
```

**Run the service:**
```bash
python scripts/embedding_service.py
```

This will start the embedding API at `http://localhost:8000/embed`

### 2. n8n Instance

Your n8n instance should be running at `https://flow.imurph.com` (already configured based on your MCP setup).

### 3. Database Setup

Ensure your Neon Postgres database has:
- `pgvector` extension enabled
- `cv_chunks` table created (see `docs/setup_database.sql`)
- Embeddings populated (run `python scripts/embedder.py`)

### 4. Ollama on VPS

Verify Ollama is running and accessible:
```bash
curl http://your-vps-ip:11434/api/generate \
  -d '{"model": "llama3.2:latest", "prompt": "Hello", "stream": false}'
```

## Import Workflow into n8n

### Step 1: Import JSON

1. Log into n8n at `https://flow.imurph.com`
2. Click **Workflows** → **Import from File**
3. Select `n8n/cv-rag-workflow.json`
4. Click **Import**

### Step 2: Configure Credentials

The workflow requires Neon Postgres credentials:

1. Click on the **Postgres Vector Search** node
2. Click **Create New Credential**
3. Enter your Neon connection details:
   - **Host**: `your-project.neon.tech`
   - **Database**: `your-database-name`
   - **User**: `your-username`
   - **Password**: `your-password`
   - **SSL**: Enable (required for Neon)
   - **Port**: `5432`
4. Click **Save**

### Step 3: Configure Environment Variables

In n8n, set these environment variables (Settings → Environments):

- `OLLAMA_API_URL`: `http://your-vps-ip:11434`
- `OLLAMA_MODEL`: `llama3.2:latest`

Alternatively, you can hardcode these in the **Ollama - Generate Answer** node.

### Step 4: Update Embedding Service URL

In the **Generate Query Embedding** node:
- If running locally: Keep `http://localhost:8000/embed`
- If embedding service is on VPS: Update to `http://your-vps-ip:8000/embed`

### Step 5: Activate Workflow

1. Click the **Inactive** toggle in the top-right to activate the workflow
2. The webhook will now be available at:
   ```
   https://flow.imurph.com/webhook/cv-rag-query
   ```

### Step 6: Update .env File

Copy the webhook URL and update your `.env` file:

```bash
N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query
```

## Testing the Workflow

### Test 1: Direct Webhook Test

```bash
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What programming languages does Mike know?"
  }'
```

Expected response:
```json
{
  "answer": "Based on the resume context, Mike has experience with...",
  "query": "What programming languages does Mike know?",
  "chunks_used": 3,
  "model": "llama3.2:latest",
  "timestamp": "2025-11-03T12:34:56.789Z"
}
```

### Test 2: Using Python Script

```bash
python scripts/query.py
```

This script (from your existing codebase) should now work with the n8n workflow.

### Test 3: Streamlit Frontend

```bash
streamlit run streamlit/app.py
```

The Streamlit app will send queries to the n8n webhook and display responses.

## Workflow Nodes Explained

### 1. Webhook - Receive Query
- **Type**: Webhook Trigger
- **Method**: POST
- **Path**: `cv-rag-query`
- **Input**: `{ "query": "user question" }`

### 2. Generate Query Embedding
- **Type**: HTTP Request
- **URL**: `http://localhost:8000/embed`
- **Purpose**: Converts query text to 384-dimensional vector
- **Output**: `{ "embedding": [0.123, -0.456, ...], "dimension": 384 }`

### 3. Postgres Vector Search
- **Type**: Postgres Node
- **Operation**: Execute Query
- **SQL**: Uses pgvector `<=>` operator for cosine similarity
- **Output**: Top 3 most similar chunks with similarity scores

### 4. Format Context for LLM
- **Type**: Code (JavaScript)
- **Purpose**: Combines retrieved chunks into structured prompt
- **Output**: System prompt + user prompt with context

### 5. Ollama - Generate Answer
- **Type**: HTTP Request
- **URL**: `{OLLAMA_API_URL}/api/generate`
- **Purpose**: Calls Ollama LLM with context-enhanced prompt
- **Parameters**:
  - Model: `llama3.2:latest`
  - Temperature: `0.7`
  - Max tokens: `500`

### 6. Format Final Response
- **Type**: Code (JavaScript)
- **Purpose**: Structures the final JSON response for Streamlit

### 7. Respond to Webhook
- **Type**: Respond to Webhook
- **Purpose**: Sends JSON response back to the client

## Troubleshooting

### Embedding Service Not Running
**Error**: `Connection refused on localhost:8000`

**Fix**:
```bash
python scripts/embedding_service.py
```

### Postgres Connection Failed
**Error**: `FATAL: password authentication failed`

**Fix**:
- Verify Neon credentials in n8n
- Check if Neon database is suspended (free tier)
- Ensure SSL is enabled in credentials

### Ollama Timeout
**Error**: `Request timeout after 60000ms`

**Fix**:
- Verify Ollama is running: `systemctl status ollama`
- Check firewall allows port 11434
- Test direct access: `curl http://vps-ip:11434`

### No Chunks Retrieved
**Error**: `chunks_used: 0`

**Fix**:
- Verify embeddings are in database: `SELECT COUNT(*) FROM cv_chunks;`
- Run embedder: `python scripts/embedder.py`
- Check vector dimension matches (384)

### Workflow Execution Fails
**Error**: Various node errors

**Fix**:
- Check n8n execution logs (click on failed execution)
- Test each node individually using "Test workflow" button
- Verify all credentials are saved

## Performance Optimization

### For Production:
1. **Cache embeddings**: Store frequently asked queries
2. **Batch processing**: Process multiple queries simultaneously
3. **Connection pooling**: Configure Postgres connection limits
4. **Ollama optimization**: Increase VPS resources or use quantized models
5. **Rate limiting**: Add rate limiting to webhook to prevent abuse

## Next Steps

1. ✅ Import workflow into n8n
2. ✅ Configure credentials and environment variables
3. ✅ Start embedding service
4. ✅ Test workflow with sample queries
5. ✅ Integrate with Streamlit frontend
6. 📝 Monitor execution logs for errors
7. 📝 Add analytics tracking (optional)
8. 📝 Deploy to production

## Workflow Export

To export your configured workflow (for backup or version control):

1. Open workflow in n8n
2. Click **⋮** (three dots) → **Download**
3. **IMPORTANT**: Remove sensitive data before committing:
   - Postgres credentials
   - API keys
   - VPS IP addresses

## Support

For issues or questions:
- Check n8n documentation: https://docs.n8n.io
- Review CLAUDE.md for project-specific details
- Test components individually before full pipeline
