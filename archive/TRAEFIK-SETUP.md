# CV-RAG with Traefik on app-net

Quick reference for deploying CV-RAG Streamlit to your existing Traefik + n8n + Ollama setup.

## Your Current Setup

- **Traefik**: Reverse proxy handling HTTPS
- **n8n**: Running at `https://flow.imurph.com` (has its own docker-compose.yml)
- **Ollama**: Running on VPS (has its own docker-compose.yml)
- **Docker Network**: `app-net` (shared by n8n, Ollama, Traefik, and now Streamlit)

## Architecture

```
Internet
   │
   ▼
Traefik (HTTPS)
   │
   ├──▶ https://flow.imurph.com ──▶ n8n container
   │                                    │
   └──▶ https://chat.imurph.com ──▶ Streamlit container
                                        │
                                        ▼
                                    (all on app-net)
                                        │
                                        ▼
                                    Ollama container
```

## Deployment Steps

### 1. Transfer Files to VPS

From your Mac:
```bash
cd ~/Code/Projects/cv-rag
git add .
git commit -m "Add Streamlit Docker deployment with Traefik support"
git push origin main
```

On VPS:
```bash
sudo mkdir -p /cv-rag
sudo chown $USER:$USER /cv-rag
cd /cv-rag
git clone https://github.com/mikemurphyco/cv-rag.git .
```

### 2. Configure Environment

```bash
cd /cv-rag
cp .env.example .env
nano .env
```

Update these values:
```env
# n8n Configuration (already running at flow.imurph.com)
N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query
N8N_HOST=flow.imurph.com

# Neon Database
NEON_CONNECTION_STRING=postgresql://user:pass@host.neon.tech/db?sslmode=require

# Optional (if needed)
N8N_BASIC_AUTH_USER=your-username
N8N_BASIC_AUTH_PASSWORD=your-password
```

### 3. Deploy Streamlit Container

```bash
cd /cv-rag
docker-compose up -d
```

This will:
- Build the Streamlit container
- Connect it to the existing `app-net` network
- Configure Traefik labels for `chat.imurph.com`
- Traefik will automatically provision SSL certificate

### 4. Verify Deployment

```bash
# Check container is running
docker ps | grep cv-rag-streamlit

# View logs
docker-compose logs -f streamlit

# Check it's on app-net
docker network inspect app-net | grep cv-rag-streamlit
```

### 5. Import n8n Workflows

1. Open `https://flow.imurph.com` in browser
2. Log in to n8n
3. Import `n8n/workflow-1-document-ingestion.json`
4. Import `n8n/workflow-2-query-pipeline.json`
5. Configure Postgres credentials in both workflows
6. Update Ollama node base URLs to match your container name (e.g., `http://ollama:11434`)
7. Activate both workflows
8. Copy webhook URL from Workflow 2's "Webhook (for Streamlit)" node

### 6. Update Streamlit with Webhook URL

```bash
nano .env
# Update N8N_WEBHOOK_URL with the actual webhook URL
# Example: N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query

# Restart Streamlit
docker-compose restart streamlit
```

### 7. Test Everything

**Access Streamlit:**
```bash
# Should automatically redirect to HTTPS via Traefik
open https://chat.imurph.com
```

**Test n8n Workflow 2 in Chat Panel:**
1. Open Workflow 2 in n8n
2. Click "Open Chat" button
3. Ask: "What AI tutorials has Mike created?"
4. Verify response

**Test Streamlit → n8n Integration:**
1. Open `https://chat.imurph.com`
2. Click a sample question or type your own
3. Verify response appears

## Traefik Configuration

The `docker-compose.yml` includes these Traefik labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.cv-rag-chat.rule=Host(`chat.imurph.com`)"
  - "traefik.http.routers.cv-rag-chat.entrypoints=websecure"
  - "traefik.http.routers.cv-rag-chat.tls.certresolver=letsencrypt"
  - "traefik.http.services.cv-rag-chat.loadbalancer.server.port=8501"
  - "traefik.docker.network=app-net"
```

**Important:** Make sure:
- DNS for `chat.imurph.com` points to your VPS IP
- Traefik is configured with Let's Encrypt cert resolver named `letsencrypt`
- Traefik's `websecure` entrypoint is configured (usually port 443)

## Network Connectivity

Since all services are on `app-net`:

- **Streamlit → n8n**: `https://flow.imurph.com/webhook/cv-rag-query` (via Traefik)
- **n8n → Ollama**: `http://ollama:11434` (direct container communication)
- **n8n → Neon DB**: Via internet (connection string in n8n credentials)

## Troubleshooting

### Streamlit container can't reach n8n

Check if both containers are on app-net:
```bash
docker network inspect app-net
```

Should show both `cv-rag-streamlit` and your n8n container.

### Traefik not routing to Streamlit

Check Traefik logs:
```bash
docker logs traefik
```

Verify Traefik can see the container:
```bash
docker exec traefik cat /etc/traefik/traefik.yml
```

### SSL certificate not provisioning

Check DNS:
```bash
dig chat.imurph.com +short
# Should return your VPS IP
```

Check Traefik cert resolver:
```bash
docker logs traefik | grep letsencrypt
```

### n8n workflows can't reach Ollama

Update Ollama base URL in n8n nodes. It should be the container name on app-net, such as:
- `http://ollama:11434` (if your Ollama container is named "ollama")
- `http://cv-rag-ollama:11434` (if using the full docker-compose)

Check your Ollama container name:
```bash
docker ps | grep ollama
```

## Management Commands

```bash
# View all containers on app-net
docker network inspect app-net

# View Streamlit logs
docker-compose logs -f streamlit

# Restart Streamlit
docker-compose restart streamlit

# Stop Streamlit
docker-compose down

# Update and rebuild
git pull
docker-compose down
docker-compose up -d --build

# Check Traefik routes
docker exec traefik wget -qO- http://localhost:8080/api/http/routers
```

## Ingest Documents (One-Time Setup)

After workflows are imported and activated:

```bash
# Clean existing data (optional)
python3 scripts/clean_database.py

# Run Workflow 1 to ingest documents
# Either:
# 1. Click "Execute Workflow" in n8n UI for Workflow 1, or
# 2. Use the workflow's webhook trigger (if configured)

# Verify chunks were created
psql "$NEON_CONNECTION_STRING" -c "SELECT COUNT(*) FROM cv_chunks;"
# Should show ~27 chunks
```

## DNS Setup

Make sure you have DNS A records:
- `flow.imurph.com` → Your VPS IP (existing)
- `chat.imurph.com` → Your VPS IP (new)

Traefik will automatically provision SSL certificates for both.

## Note on Service Management

Each service has its own docker-compose.yml:
- **n8n**: Managed by its own compose file
- **Ollama**: Managed by its own compose file
- **Streamlit**: Managed by `/cv-rag/docker-compose.yml` (this project)

All services connect via the shared `app-net` Docker network for inter-service communication.

## Next Steps

1. ✅ Deploy Streamlit container
2. ✅ Import n8n workflows
3. ✅ Configure webhook URL
4. ✅ Ingest documents via Workflow 1
5. ✅ Test queries via Streamlit
6. 🎥 Record demo video
7. 📝 Write tutorial blog post
8. 🚀 Share on LinkedIn/Twitter

## Resources

- Main deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Transfer guide: [TRANSFER.md](TRANSFER.md)
- Project docs: [CLAUDE.md](CLAUDE.md)
- n8n setup: [n8n/README.md](n8n/README.md)
