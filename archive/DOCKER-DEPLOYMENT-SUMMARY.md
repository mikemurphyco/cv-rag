# Docker Deployment Summary

## What We Just Built

Complete Docker deployment setup for CV-RAG Streamlit frontend, configured to work with your existing Traefik + n8n + Ollama infrastructure.

## Files Created

### Docker Configuration
1. **`streamlit/Dockerfile`** - Container image for Streamlit app
   - Python 3.11-slim base
   - Installs dependencies from requirements.txt
   - Exposes port 8501
   - Health check endpoint

2. **`streamlit/requirements.txt`** - Python dependencies
   - streamlit, requests, python-dotenv, pandas
   - Minimal set for production

3. **`streamlit/.streamlit/config.toml`** - Streamlit configuration
   - Dark theme
   - Headless server mode
   - Security settings

4. **`docker-compose.yml`** - Streamlit deployment
   - Connects to existing `app-net` network (shared with your n8n and Ollama)
   - Traefik labels for `chat.imurph.com`
   - Auto-SSL via Let's Encrypt
   - Works alongside your existing n8n and Ollama compose files

### Environment Configuration
6. **`.env.example`** - Updated with Traefik/Docker settings
   - n8n webhook URL (https://flow.imurph.com)
   - Docker network configuration
   - Traefik-specific settings

### Documentation
7. **`DEPLOYMENT.md`** - Updated comprehensive deployment guide
   - Architecture diagram with Traefik
   - Two deployment options (Streamlit-only vs full stack)
   - Step-by-step instructions

8. **`TRANSFER.md`** - File transfer guide
   - Three methods: Git, rsync, scp
   - VPS setup instructions
   - Post-transfer configuration

9. **`TRAEFIK-SETUP.md`** - Traefik-specific quick start
   - Your exact setup (app-net, flow.imurph.com)
   - Streamlined deployment steps
   - Network connectivity guide
   - Troubleshooting for Traefik issues

10. **`setup-vps.sh`** - Automated VPS setup script
    - Creates `/cv-rag` directory
    - Checks/installs Docker
    - Provides next-step instructions

### n8n Workflow Updates
11. **`n8n/workflow-2-query-pipeline.json`** - Updated with dual triggers
    - **Chat Trigger**: For testing in n8n UI
    - **Webhook**: For Streamlit API calls
    - **Respond to Webhook** node: Returns JSON

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Internet                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │    Traefik     │ (HTTPS, SSL)
            │  Reverse Proxy │
            └───┬────────┬───┘
                │        │
    ┌───────────┘        └───────────┐
    │                                 │
    ▼                                 ▼
┌─────────────┐              ┌──────────────┐
│  Streamlit  │              │     n8n      │
│chat.imurph  │──(webhook)──▶│ flow.imurph  │
│   :8501     │              │    :5678     │
└─────────────┘              └──────┬───────┘
                                    │
                            ┌───────▼───────┐     ┌────────────┐
                            │    Ollama     │────▶│   Neon     │
                            │  (Internal)   │     │  Postgres  │
                            │   :11434      │     │  (Cloud)   │
                            └───────────────┘     └────────────┘
                                                          │
                                                   pgvector DB

        All services connected via 'app-net' Docker network
```

## How It Works

1. **User visits `https://chat.imurph.com`**
   - Traefik routes to Streamlit container
   - SSL automatically handled by Let's Encrypt

2. **User asks a question in Streamlit**
   - Streamlit POSTs to `https://flow.imurph.com/webhook/cv-rag-query`
   - n8n receives webhook, triggers Workflow 2

3. **n8n processes query**
   - Embeddings Ollama node: Converts query to vector (via `http://ollama:11434`)
   - Postgres Vector Store: Retrieves top 5 similar chunks from Neon
   - Ollama Chat Model: Generates answer using llama3.2 (via `http://ollama:11434`)
   - Respond to Webhook node: Returns JSON response

4. **Streamlit displays answer**
   - Receives JSON from n8n
   - Shows answer to user

## Key Configuration Details

### Network: `app-net`
All services communicate on this shared Docker network:
- Streamlit container: `cv-rag-streamlit`
- n8n (your existing container)
- Ollama (your existing container)
- Traefik (your existing container)

### Traefik Labels
Streamlit container includes these labels:
```yaml
traefik.enable=true
traefik.http.routers.cv-rag-chat.rule=Host(`chat.imurph.com`)
traefik.http.routers.cv-rag-chat.entrypoints=websecure
traefik.http.routers.cv-rag-chat.tls.certresolver=letsencrypt
traefik.http.services.cv-rag-chat.loadbalancer.server.port=8501
traefik.docker.network=app-net
```

### Environment Variables
Required in `.env`:
- `N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query`
- `NEON_CONNECTION_STRING=postgresql://...`

Optional (already set in n8n):
- `N8N_BASIC_AUTH_USER`
- `N8N_BASIC_AUTH_PASSWORD`

## Deployment Commands

### Quick Start (Streamlit Only)
```bash
# On VPS
cd /cv-rag
cp .env.example .env
nano .env  # Update N8N_WEBHOOK_URL and NEON_CONNECTION_STRING
docker-compose up -d
```

### Only Streamlit
Since n8n and Ollama have their own docker-compose files, you only need to deploy Streamlit:
```bash
cd /cv-rag
docker-compose up -d
```

### Management
```bash
# All commands run from /cv-rag directory

# View logs
docker-compose logs -f streamlit

# Restart Streamlit only
docker-compose restart streamlit

# Stop Streamlit only
docker-compose down

# Update Streamlit
git pull && docker-compose up -d --build

# Note: n8n and Ollama are managed separately via their own compose files
```

## Pre-Deployment Checklist

- [ ] DNS: `chat.imurph.com` A record points to VPS IP
- [ ] Traefik: Running and configured with Let's Encrypt
- [ ] Docker: `app-net` network exists (`docker network inspect app-net`)
- [ ] n8n: Running at `https://flow.imurph.com`
- [ ] Ollama: Running with models loaded (`ollama list`)
- [ ] Neon: Database created with pgvector extension

## Post-Deployment Steps

1. Import n8n workflows (Workflow 1 and 2)
2. Configure Postgres credentials in both workflows
3. Update Ollama base URLs in workflow nodes to match your container names
4. Activate both workflows
5. Copy webhook URL from Workflow 2
6. Update `.env` with webhook URL
7. Restart Streamlit: `docker-compose restart streamlit`
8. Run Workflow 1 to ingest documents
9. Test queries in Streamlit at `https://chat.imurph.com`

## Testing

### Test n8n Workflow
```bash
curl -X POST https://flow.imurph.com/webhook/cv-rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What AI tutorials has Mike created?"}'
```

### Test Streamlit
1. Open `https://chat.imurph.com`
2. Click a sample question
3. Verify response appears

### Test Network Connectivity
```bash
# Check Streamlit container can reach n8n
docker exec cv-rag-streamlit curl -I https://flow.imurph.com

# Check all containers on app-net
docker network inspect app-net
```

## Troubleshooting

### Streamlit can't reach n8n
- Verify both containers on `app-net`: `docker network inspect app-net`
- Check webhook URL in `.env` matches n8n workflow
- Test webhook directly with curl

### Traefik not routing to Streamlit
- Check DNS: `dig chat.imurph.com +short`
- Check Traefik logs: `docker logs traefik`
- Verify labels are correct: `docker inspect cv-rag-streamlit`

### SSL certificate not working
- Wait a few minutes for Let's Encrypt provisioning
- Check Traefik logs for cert errors
- Verify DNS is propagated

### n8n can't reach Ollama
- Check Ollama container name: `docker ps | grep ollama`
- Update n8n Ollama nodes with correct URL (e.g., `http://ollama:11434`)
- Verify both on same network: `docker network inspect app-net`

## Files You'll Edit

When deploying, you'll need to edit:
1. **`.env`** - Add your actual credentials and URLs
2. **n8n workflows** - Configure Postgres credentials and Ollama URLs after import

Everything else is ready to go!

## Next Steps

See **[TRAEFIK-SETUP.md](TRAEFIK-SETUP.md)** for step-by-step deployment instructions tailored to your setup.

## Resources

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[TRANSFER.md](TRANSFER.md)** - File transfer methods
- **[TRAEFIK-SETUP.md](TRAEFIK-SETUP.md)** - Traefik-specific guide
- **[CLAUDE.md](CLAUDE.md)** - Project documentation
- **[n8n/README.md](n8n/README.md)** - n8n workflow setup
