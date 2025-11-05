# CV-RAG Deployment Guide

This guide covers deploying the CV-RAG system on your VPS using Docker with Traefik reverse proxy.

## Architecture Overview

```
                                    ┌─────────────┐
                                    │   Traefik   │
                                    │   (HTTPS)   │
                                    └──────┬──────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                              │
            ┌───────▼───────┐                              ┌──────▼──────┐
            │   Streamlit   │                              │     n8n     │
            │ chat.imurph.com│────────────────────────────▶│flow.imurph.com│
            │    :8501      │    Webhook API calls        │    :5678    │
            └───────────────┘                              └──────┬──────┘
                                                                  │
                                                           ┌──────▼──────┐     ┌─────────────┐
                                                           │   Ollama    │     │    Neon     │
                                                           │  (Internal) │────▶│  Postgres   │
                                                           │   :11434    │     │   (Cloud)   │
                                                           └─────────────┘     └─────────────┘
                                                                                      │
                                                                               pgvector embeddings
```

## Deployment Options

This project supports two deployment scenarios:

1. **Streamlit Only** (Recommended if n8n/Ollama already running)
   - Use `docker-compose.yml`
   - Only deploys Streamlit container
   - Connects to existing n8n at `https://flow.imurph.com`

2. **Full Stack**
   - Use `docker-compose.full.yml`
   - Deploys Streamlit, n8n, and Ollama together
   - All services behind Traefik with automatic SSL

## Prerequisites

1. **VPS Requirements**
   - Ubuntu 20.04+ (or similar Linux distribution)
   - Minimum 8GB RAM (for Ollama models)
   - Minimum 2 vCPUs
   - 20GB+ available disk space
   - Docker and Docker Compose installed

2. **External Services**
   - Neon Postgres database with pgvector extension enabled
   - Domain name pointed to your VPS (optional, for HTTPS)

3. **Local Requirements**
   - Git installed
   - SSH access to your VPS

## Step 1: VPS Setup

### 1.1 Install Docker

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### 1.2 Install Ollama Models

```bash
# Pull required models
docker exec cv-rag-ollama ollama pull nomic-embed-text:latest
docker exec cv-rag-ollama ollama pull llama3.2:latest

# Verify models are installed
docker exec cv-rag-ollama ollama list
```

Or if running Ollama standalone (not in Docker):

```bash
ollama pull nomic-embed-text:latest
ollama pull llama3.2:latest
ollama list
```

## Step 2: Clone Repository

```bash
# Clone the repository
cd ~
git clone https://github.com/yourusername/cv-rag.git
cd cv-rag
```

## Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

Required values to update:
- `N8N_WEBHOOK_URL`: Your n8n webhook URL (e.g., `https://flow.yourdomain.com/webhook/cv-rag-query`)
- `N8N_BASIC_AUTH_USER`: Choose a username for n8n access
- `N8N_BASIC_AUTH_PASSWORD`: Choose a strong password
- `N8N_HOST`: Your domain name (e.g., `flow.yourdomain.com`)
- `NEON_CONNECTION_STRING`: Your Neon Postgres connection string

## Step 4: Start Docker Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

Expected output:
```
NAME                  STATUS
cv-rag-streamlit      Up (healthy)
cv-rag-n8n            Up (healthy)
cv-rag-ollama         Up (healthy)
```

## Step 5: Import n8n Workflows

### 5.1 Access n8n

1. Open your browser and navigate to `http://your-vps-ip:5678`
2. Log in with credentials from `.env` file

### 5.2 Import Workflow 1 (Document Ingestion)

1. Click "Add workflow" → "Import from file"
2. Select `n8n/workflow-1-document-ingestion.json`
3. Configure Postgres credentials:
   - Click on "Postgres Vector Store" node
   - Add credential: Use `NEON_CONNECTION_STRING` from `.env`
   - Enable SSL
4. Update Ollama base URL (if needed):
   - Click on "Embeddings Ollama" node
   - Set base URL to `http://ollama:11434` (if using Docker)
5. Click "Save" and "Activate"

### 5.3 Import Workflow 2 (Query Pipeline)

1. Click "Add workflow" → "Import from file"
2. Select `n8n/workflow-2-query-pipeline.json`
3. Configure Postgres credentials (same as Workflow 1)
4. Update Ollama base URLs:
   - "Embeddings Ollama" node: `http://ollama:11434`
   - "Ollama Chat Model" node: `http://ollama:11434`
5. Note the webhook URL for later:
   - Click on "Webhook (for Streamlit)" node
   - Copy the "Production URL" (e.g., `https://flow.yourdomain.com/webhook/cv-rag-query`)
6. Click "Save" and "Activate"

### 5.4 Update Streamlit Environment

```bash
# Update N8N_WEBHOOK_URL in .env with the webhook URL from step 5.3
nano .env

# Restart Streamlit container to pick up new environment variable
docker-compose restart streamlit
```

## Step 6: Ingest Documents

### 6.1 Test Workflow 1

1. In n8n, open Workflow 1
2. Click "Execute Workflow" (or use the webhook trigger)
3. Verify chunks are created:

```bash
# Connect to your Neon database and check
psql "$NEON_CONNECTION_STRING" -c "SELECT COUNT(*) FROM cv_chunks;"
```

Expected output: ~27 chunks

## Step 7: Test the System

### 7.1 Test n8n Query Workflow

1. In n8n, open Workflow 2
2. Click "Open Chat" (Chat Trigger)
3. Ask: "What AI tutorials has Mike created?"
4. Verify you get a detailed response

### 7.2 Test Streamlit Frontend

1. Open browser to `http://your-vps-ip:8501`
2. Click a sample question or type your own
3. Verify response appears

## Step 8: Set Up HTTPS (Optional but Recommended)

### 8.1 Install Nginx and Certbot

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 8.2 Configure Nginx for n8n

```bash
sudo nano /etc/nginx/sites-available/n8n
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name flow.yourdomain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8.3 Configure Nginx for Streamlit

```bash
sudo nano /etc/nginx/sites-available/streamlit
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name chat.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8.4 Get SSL Certificates

```bash
sudo certbot --nginx -d flow.yourdomain.com -d chat.yourdomain.com
```

Follow the prompts to complete setup.

## Step 9: Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit
docker-compose logs -f n8n
docker-compose logs -f ollama
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart streamlit
```

### Update Application

```bash
cd ~/cv-rag
git pull
docker-compose down
docker-compose up -d --build
```

### Re-ingest Documents

If you update your resume or supplemental materials:

```bash
# Option 1: Run cleanup script first
python3 scripts/clean_database.py

# Option 2: Delete directly in SQL
psql "$NEON_CONNECTION_STRING" -c "DELETE FROM cv_chunks;"

# Then re-run Workflow 1 in n8n
```

### Backup

```bash
# Backup n8n data
docker exec cv-rag-n8n n8n export:workflow --backup --output=/backup/

# Backup database (from Neon console or pg_dump)
pg_dump "$NEON_CONNECTION_STRING" > backup.sql
```

## Troubleshooting

### Streamlit can't connect to n8n

1. Verify n8n workflow is active
2. Check webhook URL in `.env` matches n8n
3. Test webhook directly:
   ```bash
   curl -X POST https://flow.yourdomain.com/webhook/cv-rag-query \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'
   ```

### Ollama timeout errors

1. Check Ollama is running: `docker ps | grep ollama`
2. Verify models are loaded: `docker exec cv-rag-ollama ollama list`
3. Check memory usage: `docker stats`

### No AI nodes in n8n

Update n8n to latest version:
```bash
docker-compose pull n8n
docker-compose up -d n8n
```

### Database connection issues

1. Verify connection string in `.env`
2. Check pgvector extension:
   ```sql
   psql "$NEON_CONNECTION_STRING" -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```
3. Check firewall allows Neon connection

## Performance Optimization

### 1. Resource Allocation

Edit `docker-compose.yml` to adjust resource limits:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 6G
```

### 2. Ollama Model Selection

For lower resource usage, consider smaller models:
```bash
ollama pull llama3.2:1b  # Smaller, faster model
```

### 3. Caching

Enable n8n workflow caching in workflow settings to reduce redundant calls.

## Next Steps

1. **Monitor Performance**: Use `docker stats` to monitor resource usage
2. **Set Up Backups**: Schedule regular backups of n8n workflows and database
3. **Analytics**: Add logging/analytics to track popular queries
4. **Content Updates**: Keep resume materials updated in GitHub
5. **Security**: Review and harden authentication, enable rate limiting

## Support

- Project Repository: https://github.com/yourusername/cv-rag
- n8n Documentation: https://docs.n8n.io
- Ollama Documentation: https://ollama.ai/docs
- Streamlit Documentation: https://docs.streamlit.io

## License

This project is for demonstration and educational purposes.
