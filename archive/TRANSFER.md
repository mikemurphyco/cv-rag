# Transferring CV-RAG to VPS

Quick guide for moving your CV-RAG project from your Mac to your VPS.

## Option 1: Using Git (Recommended)

### On Mac (Local)
```bash
# Commit all changes
cd ~/Code/Projects/cv-rag
git add .
git commit -m "Add Docker deployment configuration"
git push origin main
```

### On VPS
```bash
# Create directory
sudo mkdir -p /cv-rag
sudo chown $USER:$USER /cv-rag

# Clone repository
cd /cv-rag
git clone https://github.com/yourusername/cv-rag.git .

# Configure environment
cp .env.example .env
nano .env  # Add your actual values
```

## Option 2: Using rsync (Direct File Transfer)

### On Mac (Local)
```bash
# Transfer files directly from Mac to VPS
rsync -avz --progress \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.env' \
  --exclude 'node_modules' \
  ~/Code/Projects/cv-rag/ \
  root@your-vps-ip:/cv-rag/
```

### On VPS
```bash
# Set proper ownership
sudo chown -R $USER:$USER /cv-rag

# Configure environment
cd /cv-rag
cp .env.example .env
nano .env  # Add your actual values
```

## Option 3: Using SCP (Simple Copy)

### On Mac (Local)
```bash
# Create a tarball (excluding unnecessary files)
cd ~/Code/Projects/cv-rag
tar --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.env' \
    -czf cv-rag.tar.gz .

# Copy to VPS
scp cv-rag.tar.gz root@your-vps-ip:/tmp/

# Clean up local tarball
rm cv-rag.tar.gz
```

### On VPS
```bash
# Create directory and extract
sudo mkdir -p /cv-rag
cd /cv-rag
sudo tar -xzf /tmp/cv-rag.tar.gz
sudo chown -R $USER:$USER /cv-rag
rm /tmp/cv-rag.tar.gz

# Configure environment
cp .env.example .env
nano .env  # Add your actual values
```

## After Transfer: VPS Setup

### 1. Install Docker (if not already installed)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt update
sudo apt install -y docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
```

### 2. Configure Environment Variables

```bash
cd /cv-rag
nano .env
```

Required values:
- `N8N_WEBHOOK_URL` - Will get this after importing workflows
- `N8N_BASIC_AUTH_USER` - Your choice (e.g., "admin")
- `N8N_BASIC_AUTH_PASSWORD` - Strong password
- `N8N_HOST` - Your domain (e.g., "flow.yourdomain.com")
- `NEON_CONNECTION_STRING` - From Neon console

### 3. Start Services

```bash
cd /cv-rag
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Pull Ollama Models

```bash
# Wait for Ollama to start (check logs)
docker-compose logs -f ollama

# Pull models (in a new terminal)
docker exec cv-rag-ollama ollama pull nomic-embed-text:latest
docker exec cv-rag-ollama ollama pull llama3.2:latest

# Verify
docker exec cv-rag-ollama ollama list
```

### 5. Import n8n Workflows

1. Open browser: `http://your-vps-ip:5678`
2. Log in with credentials from `.env`
3. Import `n8n/workflow-1-document-ingestion.json`
4. Import `n8n/workflow-2-query-pipeline.json`
5. Configure Postgres credentials in both workflows
6. Update Ollama URLs to `http://ollama:11434`
7. Activate both workflows
8. Copy webhook URL from Workflow 2

### 6. Update Streamlit Configuration

```bash
# Add webhook URL to .env
nano .env
# Update: N8N_WEBHOOK_URL=https://your-domain.com/webhook/cv-rag-query

# Restart Streamlit
docker-compose restart streamlit
```

### 7. Test Everything

```bash
# Test Streamlit
curl http://localhost:8501

# Test n8n
curl http://localhost:5678

# Test Ollama
docker exec cv-rag-ollama ollama list
```

Open in browser:
- Streamlit: `http://your-vps-ip:8501`
- n8n: `http://your-vps-ip:5678`

## Directory Structure on VPS

After setup, your VPS should have:

```
/cv-rag/
├── docker-compose.yml
├── .env (your actual values)
├── .env.example
├── DEPLOYMENT.md
├── TRANSFER.md
├── streamlit/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── .streamlit/
│       └── config.toml
├── n8n/
│   ├── workflow-1-document-ingestion.json
│   └── workflow-2-query-pipeline.json
├── docs/
│   ├── cv_mike-murphy.md
│   └── supplemental.md
└── scripts/
    └── clean_database.py
```

## Quick Commands Reference

```bash
# View all logs
docker-compose logs -f

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Update from Git
git pull
docker-compose down
docker-compose up -d --build

# Check service health
docker-compose ps
docker stats
```

## Next Steps

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Setting up HTTPS with Nginx
- Domain configuration
- SSL certificates with Let's Encrypt
- Production optimization
- Monitoring and maintenance

## Troubleshooting

### Permission Issues
```bash
sudo chown -R $USER:$USER /cv-rag
```

### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :8501  # Streamlit
sudo lsof -i :5678  # n8n
sudo lsof -i :11434 # Ollama
```

### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose up -d --build --force-recreate

# Clean up old containers/images
docker system prune -a
```
