# CV-RAG Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CV-RAG System Architecture                   │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
       │
       │ Query
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Streamlit Frontend                              │
│                    (streamlit/app.py)                                 │
│  - Sample question buttons                                            │
│  - Chat interface                                                     │
│  - Response display                                                   │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       │ HTTP POST {"query": "..."}
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       n8n Workflow Orchestrator                       │
│                   (https://flow.imurph.com)                           │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 1. Webhook Trigger                                           │    │
│  │    - Receives POST request with user query                   │    │
│  │    - Path: /webhook/cv-rag-query                             │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 2. Generate Query Embedding                                  │    │
│  │    - HTTP Request to embedding service                       │    │
│  │    - URL: http://localhost:8000/embed                        │    │
│  │    - Returns: 384-dim vector                                 │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 3. Postgres Vector Search                                    │    │
│  │    - Executes pgvector similarity query                      │    │
│  │    - Returns top 3 most relevant chunks                      │    │
│  │    - Uses cosine distance (<=>)                              │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 4. Format Context for LLM                                    │    │
│  │    - JavaScript Code Node                                    │    │
│  │    - Combines chunks into structured prompt                  │    │
│  │    - Adds system prompt and instructions                     │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 5. Ollama LLM Generation                                     │    │
│  │    - HTTP Request to VPS Ollama                              │    │
│  │    - Model: llama3.2:latest                                   │    │
│  │    - Temperature: 0.7, Max tokens: 500                       │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 6. Format Final Response                                     │    │
│  │    - JavaScript Code Node                                    │    │
│  │    - Structures JSON response                                │    │
│  └───────────────────────┬─────────────────────────────────────┘    │
│                          │                                            │
│                          ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 7. Respond to Webhook                                        │    │
│  │    - Returns JSON to Streamlit                               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└──────────────────────┬────────────────────────────────────────────┬──┘
                       │                                             │
                       │ Calls                                       │ Calls
                       ▼                                             ▼
         ┌──────────────────────────┐              ┌──────────────────────────┐
         │  Embedding Service       │              │  Ollama on VPS           │
         │  (localhost:8000)        │              │  (vps-ip:11434)          │
         │                          │              │                          │
         │  - Flask HTTP server     │              │  - llama3.2:latest model │
         │  - sentence-transformers │              │  - Docker container      │
         │  - all-MiniLM-L6-v2      │              │  - 8GB RAM, 2 vCPU       │
         │  - 384-dim embeddings    │              │                          │
         └──────────────────────────┘              └──────────────────────────┘

                       │ Query                        │ Retrieves
                       │ Searches                     │ Chunks
                       ▼                              │
         ┌──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Neon Postgres Database                          │
│                     (Cloud-hosted pgvector)                           │
│                                                                       │
│  Table: cv_chunks                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ id | chunk_id | content | source | embedding (vector 384)     │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ 1  | resume_0 | Mike... | resume | [0.123, -0.456, ...]      │  │
│  │ 2  | resume_1 | Exper...| resume | [0.789, 0.234, ...]       │  │
│  │ 3  | suppl_0  | YouTu...| suppl. | [-0.567, 0.890, ...]      │  │
│  │ ...                                                            │  │
│  │ 25 | suppl_12 | AI pr...| suppl. | [0.345, -0.678, ...]      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Index: ivfflat on embedding using vector_cosine_ops                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

### 1. Document Ingestion Phase (One-time setup)

```
Resume/Supplemental Docs
        │
        │ scripts/chunker.py
        ▼
    Chunks (JSON)
        │
        │ scripts/embedder.py
        ▼
  Generate Embeddings
  (sentence-transformers)
        │
        ▼
  Neon Postgres (cv_chunks table)
```

### 2. Query Processing Phase (Runtime)

```
User Query: "What programming languages does Mike know?"
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 1: Streamlit sends to n8n webhook                         │
│ POST https://flow.imurph.com/webhook/cv-rag-query              │
│ Body: {"query": "What programming languages does Mike know?"}  │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 2: n8n calls embedding service                             │
│ POST http://localhost:8000/embed                                │
│ Body: {"text": "What programming languages does Mike know?"}    │
│ Response: {"embedding": [0.123, -0.456, ...], "dimension": 384} │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 3: n8n queries Neon Postgres                               │
│ SQL: SELECT content, source,                                    │
│        1 - (embedding <=> $1::vector) AS similarity             │
│      FROM cv_chunks                                             │
│      ORDER BY embedding <=> $1::vector                          │
│      LIMIT 3;                                                   │
│                                                                 │
│ Returns top 3 chunks:                                           │
│ - Chunk 1: "...Python, JavaScript, SQL..." (similarity: 0.89)   │
│ - Chunk 2: "...TypeScript, R, Bash..." (similarity: 0.85)       │
│ - Chunk 3: "...pandas, scikit-learn..." (similarity: 0.82)      │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 4: n8n formats context for LLM                             │
│ System Prompt: "You are an AI assistant..."                     │
│ Context: [Combined chunks from Step 3]                          │
│ User Query: "What programming languages does Mike know?"        │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 5: n8n calls Ollama LLM                                    │
│ POST http://vps-ip:11434/api/generate                           │
│ Body: {                                                         │
│   "model": "llama3.2:latest",                                   │
│   "prompt": "[Context + Query]",                                │
│   "stream": false                                               │
│ }                                                               │
│                                                                 │
│ Ollama generates: "Based on the resume context, Mike has       │
│ extensive experience with Python, JavaScript, TypeScript,      │
│ SQL, R, and Bash. He also works with data science libraries    │
│ like pandas and scikit-learn..."                                │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 6: n8n formats final response                              │
│ {                                                               │
│   "answer": "Based on the resume context, Mike has...",         │
│   "query": "What programming languages does Mike know?",        │
│   "chunks_used": 3,                                             │
│   "model": "llama3.2:latest",                                   │
│   "timestamp": "2025-11-03T22:15:30.123Z"                       │
│ }                                                               │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│ Step 7: n8n returns response to Streamlit                       │
│ HTTP 200 OK                                                     │
│ Body: [JSON from Step 6]                                        │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
    Streamlit displays answer to user
```

## Component Details

### Embedding Service (scripts/embedding_service.py)

**Technology**: Flask + sentence-transformers
**Port**: 8000
**Model**: all-MiniLM-L6-v2 (384 dimensions)
**Response Time**: ~100-200ms per query

**Endpoints**:
- `GET /health` - Health check
- `POST /embed` - Generate embeddings
- `GET /` - API documentation

**Why needed**: n8n doesn't have a built-in sentence-transformers node, so we expose the model via HTTP API.

### n8n Workflow (n8n/cv-rag-workflow.json)

**7 nodes total**:
1. **Webhook** - Entry point
2. **HTTP Request** - Embedding generation
3. **Postgres** - Vector search
4. **Code** - Context formatting
5. **HTTP Request** - Ollama LLM call
6. **Code** - Response formatting
7. **Respond to Webhook** - Exit point

**Execution time**: 3-8 seconds (depends on Ollama response)

### Database Schema

```sql
CREATE TABLE cv_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,  -- 'resume' or 'supplemental'
    chunk_index INTEGER,
    total_chunks INTEGER,
    embedding VECTOR(384),        -- pgvector extension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast similarity search
CREATE INDEX ON cv_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);
```

### Streamlit Frontend (streamlit/app.py)

**Features**:
- Chat-style interface
- 6 pre-configured sample questions
- Download buttons for resume/cover letter
- Tech stack explanation in sidebar
- Error handling for network issues

**Communication**: HTTP POST to n8n webhook, displays JSON response

## Performance Characteristics

| Component | Response Time | Notes |
|-----------|--------------|-------|
| Embedding Service | 100-200ms | Local inference, cached model |
| Postgres Vector Search | 50-100ms | Indexed search on ~25 chunks |
| Ollama LLM | 2-5 seconds | VPS with 8GB RAM, 2 vCPU |
| **Total Pipeline** | **3-8 seconds** | End-to-end query processing |

## Scalability Considerations

### Current Capacity
- **Concurrent users**: 1-5 (single Ollama instance bottleneck)
- **Database size**: Optimized for <100 chunks
- **Embedding cache**: No caching (stateless)

### Optimization Options
1. **Embedding cache**: Redis cache for frequent queries
2. **Connection pooling**: Postgres connection reuse
3. **Ollama scaling**: Multiple VPS instances + load balancer
4. **Batch processing**: Group similar queries
5. **Index optimization**: Adjust `lists` parameter for larger datasets

## Security Considerations

### Current Setup
- ✅ Postgres uses SSL (Neon requirement)
- ✅ Environment variables for secrets
- ✅ n8n webhook is public (no auth)
- ⚠️ Embedding service is localhost only
- ⚠️ No rate limiting on webhook

### Production Recommendations
1. Add API key authentication to n8n webhook
2. Implement rate limiting (prevent abuse)
3. Use HTTPS for all external communication
4. Add input validation/sanitization
5. Set up monitoring/alerting for anomalies
6. Configure CORS properly for Streamlit

## Monitoring & Debugging

### Key Metrics to Track
- **n8n execution logs**: Check for node failures
- **Embedding service logs**: Monitor for errors
- **Ollama response times**: Track LLM performance
- **Database query times**: Monitor vector search speed
- **Webhook error rates**: Track failed requests

### Debug Tools
```bash
# Test embedding service
curl http://localhost:8000/health

# Test n8n webhook
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Test Ollama
curl http://vps-ip:11434/api/generate \
  -d '{"model": "llama3.2:latest", "prompt": "test", "stream": false}'

# Check database
psql $NEON_CONNECTION_STRING -c "SELECT COUNT(*) FROM cv_chunks;"

# Run full test suite
python scripts/test_workflow.py
```

## Future Enhancements

1. **Conversation history**: Store chat context for follow-up questions
2. **Multi-turn dialogue**: Maintain conversation state
3. **Source citations**: Link answers back to specific resume sections
4. **Analytics dashboard**: Track popular questions, response quality
5. **Voice interface**: Whisper STT + ElevenLabs TTS
6. **Multi-language support**: Translate queries/responses
7. **PDF generation**: Dynamic resume PDF from Markdown
8. **A/B testing**: Compare different prompts/models

---

**Version**: 1.0.0
**Last Updated**: 2025-11-03
**Maintainer**: Mike Murphy
