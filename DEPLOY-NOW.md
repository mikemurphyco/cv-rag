# Deploy CV-RAG Streamlit Now

Ultra-quick deployment guide for your existing VPS setup.

## You Already Have
✅ Traefik with `app-net` network  
✅ n8n at `https://flow.imurph.com`  
✅ Ollama running with models

## Deploy in 5 Minutes

### 1. Get Files on VPS

```bash
# On VPS
mkdir -p /cv-rag && cd /cv-rag
git clone https://github.com/mikemurphyco/cv-rag.git .
```

### 2. Configure

```bash
cp .env.example .env
nano .env
# Update N8N_WEBHOOK_URL and NEON_CONNECTION_STRING
```

### 3. Deploy

```bash
docker-compose up -d
```

### 4. Import Workflows

1. Visit `https://flow.imurph.com`
2. Import both workflow JSON files from `n8n/` folder
3. Configure Postgres credentials
4. Update Ollama URLs to your container name
5. Activate workflows
6. Copy webhook URL

### 5. Update & Restart

```bash
nano .env  # Add webhook URL
docker-compose restart streamlit
```

### 6. Add DNS

Point `chat.imurph.com` to your VPS IP

### 7. Test

Visit: `https://chat.imurph.com`

## Done!

See [TRAEFIK-SETUP.md](TRAEFIK-SETUP.md) for details.
