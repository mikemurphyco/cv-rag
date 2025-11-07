# CV-RAG Docker Deployment

Complete Docker deployment for CV-RAG Streamlit frontend.

## What This Does

Deploys a Streamlit chat interface that connects to your existing n8n + Ollama infrastructure, all behind Traefik with automatic HTTPS.

## Quick Links

- **Ultra Quick:** [DEPLOY-NOW.md](DEPLOY-NOW.md) - 5 minute deployment
- **Traefik Specific:** [TRAEFIK-SETUP.md](TRAEFIK-SETUP.md) - Your exact setup
- **Detailed:** [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- **Summary:** [DOCKER-DEPLOYMENT-SUMMARY.md](DOCKER-DEPLOYMENT-SUMMARY.md) - What was built
- **Transfer:** [TRANSFER.md](TRANSFER.md) - How to get files to VPS

## Your Setup

```
app-net Docker Network
├── Traefik (reverse proxy, HTTPS)
├── n8n (flow.imurph.com) - your existing container
├── Ollama (LLMs) - your existing container
└── Streamlit (chat.imurph.com) - NEW! This deployment
```

## Files in This Deployment

### Docker
- `streamlit/Dockerfile` - Container image
- `streamlit/requirements.txt` - Python dependencies
- `streamlit/.streamlit/config.toml` - Streamlit config
- `docker-compose.yml` - Deployment config (Streamlit only)

### Configuration
- `.env.example` - Environment template
- `setup-vps.sh` - Automated VPS setup script

### Documentation
- `DEPLOY-NOW.md` - Ultra-quick start (5 min)
- `TRAEFIK-SETUP.md` - Traefik-specific guide
- `DEPLOYMENT.md` - Comprehensive guide
- `DOCKER-DEPLOYMENT-SUMMARY.md` - Architecture & summary
- `TRANSFER.md` - File transfer options

### Workflows
- `n8n/workflow-1-document-ingestion.json` - Ingest resume
- `n8n/workflow-2-query-pipeline.json` - Answer queries (updated with webhook)

## Prerequisites

- [ ] VPS with Docker and Docker Compose
- [ ] Traefik running with `app-net` network
- [ ] n8n running at `https://flow.imurph.com`
- [ ] Ollama running with `nomic-embed-text` and `llama3.2`
- [ ] Neon Postgres database with pgvector extension
- [ ] DNS for `chat.imurph.com` pointing to VPS

## Quick Deployment

```bash
# 1. On VPS
mkdir -p /cv-rag && cd /cv-rag
git clone https://github.com/mikemurphyco/cv-rag.git .

# 2. Configure
cp .env.example .env
nano .env  # Update N8N_WEBHOOK_URL and NEON_CONNECTION_STRING

# 3. Deploy
docker-compose up -d

# 4. Import workflows in n8n, activate, get webhook URL

# 5. Update webhook URL
nano .env
docker-compose restart streamlit
```

Visit: `https://chat.imurph.com`

## Architecture

```
                      Internet
                         │
                         ▼
                   ┌──────────┐
                   │ Traefik  │ HTTPS/SSL
                   └────┬─────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
   ┌────▼────┐                    ┌────▼────┐
   │Streamlit│─────webhook────────│   n8n   │
   │ :8501   │                    │  :5678  │
   └─────────┘                    └────┬────┘
chat.imurph.com               flow.imurph.com
                                       │
                                  ┌────▼────┐     ┌────────┐
                                  │ Ollama  │────▶│  Neon  │
                                  │ :11434  │     │Postgres│
                                  └─────────┘     └────────┘
                                   (internal)       (cloud)

                 All connected via app-net Docker network
```

## How It Works

1. User visits `https://chat.imurph.com`
2. Traefik routes to Streamlit container (auto-SSL)
3. User asks question in Streamlit
4. Streamlit POSTs to `https://flow.imurph.com/webhook/cv-rag-query`
5. n8n Workflow 2 processes query:
   - Embeddings Ollama: Query → vector
   - Postgres Vector Store: Retrieve similar chunks from Neon
   - Ollama Chat Model: Generate answer with llama3.2
   - Respond to Webhook: Return JSON
6. Streamlit displays answer

## Environment Variables

Required in `.env`:
```env
N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query
NEON_CONNECTION_STRING=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

## Management

```bash
# View logs
docker-compose logs -f streamlit

# Restart
docker-compose restart streamlit

# Stop
docker-compose down

# Update
git pull && docker-compose up -d --build

# Check network
docker network inspect app-net | grep streamlit
```

## Troubleshooting

### Streamlit won't start
```bash
docker-compose logs streamlit
```

### Can't reach n8n
```bash
# Verify both on app-net
docker network inspect app-net
```

### SSL not working
- Wait 1-2 minutes for Let's Encrypt
- Check DNS: `dig chat.imurph.com +short`
- Check Traefik logs: `docker logs traefik`

### Workflow errors
- Verify Ollama container name: `docker ps | grep ollama`
- Update Ollama URLs in n8n nodes (e.g., `http://ollama:11434`)

## Testing

```bash
# Test webhook directly
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What AI tutorials has Mike created?"}'

# Test Streamlit health
curl https://chat.imurph.com/_stcore/health

# View all app-net containers
docker network inspect app-net
```

## Next Steps After Deployment

1. ✅ Streamlit deployed
2. Import n8n workflows
3. Ingest documents via Workflow 1
4. Test queries
5. Record demo video
6. Create tutorial content
7. Share project

## Support

- **Project Issues:** [GitHub Issues](https://github.com/mikemurphyco/cv-rag/issues)
- **n8n Docs:** [docs.n8n.io](https://docs.n8n.io)
- **Traefik Docs:** [doc.traefik.io](https://doc.traefik.io)
- **Streamlit Docs:** [docs.streamlit.io](https://docs.streamlit.io)

## License

Built for demonstration and educational purposes by Mike Murphy.
