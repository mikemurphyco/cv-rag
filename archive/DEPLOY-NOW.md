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

### 2. Create Streamlit Config Directory

```bash
# Create .streamlit directory for config
mkdir -p /cv-rag/streamlit/.streamlit

# Create Streamlit configuration file
cat > /cv-rag/streamlit/.streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = true
enableXsrfProtection = true
EOF
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
# Update N8N_WEBHOOK_URL and NEON_CONNECTION_STRING
```

### 4. Deploy

```bash
docker compose up -d
```

### 5. Import Workflows

1. Visit `https://flow.imurph.com`
2. Import both workflow JSON files from `n8n/` folder
3. Configure Postgres credentials
4. Update Ollama URLs to your container name
5. Activate workflows
6. Copy webhook URL

### 6. Update & Restart

```bash
nano .env  # Add webhook URL
docker compose restart streamlit
```

### 7. Add DNS

Point `chat.imurph.com` to your VPS IP

### 8. Test

Visit: `https://chat.imurph.com`

## Done!

See [TRAEFIK-SETUP.md](TRAEFIK-SETUP.md) for details.
