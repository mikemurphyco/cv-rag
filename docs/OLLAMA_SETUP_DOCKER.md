# Ollama Docker Installation Guide for Hostinger VPS

This guide installs Ollama in a Docker container with persistent volume storage.

## Prerequisites

- Hostinger VPS (KVM2: 8GB RAM recommended)
- SSH access to your VPS
- Docker already installed on VPS

## Verify Docker is Installed

```bash
ssh root@your-vps-ip
docker --version
```

If Docker isn't installed:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

---

## Installation Steps

### 1. Create Ollama Volume (Persistent Model Storage)

```bash
docker volume create ollama_models
```

This ensures your downloaded models persist across container updates.

### 2. Run Ollama Container

```bash
docker run -d \
  --name ollama \
  --restart unless-stopped \
  -p 11434:11434 \
  -v ollama_models:/root/.ollama \
  ollama/ollama
```

**What this does:**
- `-d`: Run in background (detached)
- `--name ollama`: Names the container "ollama"
- `--restart unless-stopped`: Auto-restart on VPS reboot
- `-p 11434:11434`: Expose Ollama API port
- `-v ollama_models:/root/.ollama`: Persistent volume for models
- `ollama/ollama`: Official Ollama image

### 3. Verify It's Running

```bash
docker ps | grep ollama
```

You should see:
```
CONTAINER ID   IMAGE           STATUS          PORTS
abc123def456   ollama/ollama   Up 2 seconds    0.0.0.0:11434->11434/tcp
```

### 4. Pull Your LLM Model

```bash
# Pull llama3:8b (recommended for 8GB RAM)
docker exec ollama ollama pull llama3:8b
```

This downloads ~4.7GB. Wait for completion.

**Alternative models:**
```bash
docker exec ollama ollama pull llama3.2:3b    # Smaller (2GB)
docker exec ollama ollama pull qwen2.5:7b     # Alternative
```

### 5. Test Ollama

```bash
docker exec -it ollama ollama run llama3:8b "What is RAG in AI?"
```

If you get a response, it's working! Press `Ctrl+D` to exit.

### 6. Test API Externally

From your local machine:

```bash
curl http://your-vps-ip:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Say hello",
  "stream": false
}'
```

If this fails, continue to firewall setup.

---

## Firewall Configuration

### Allow Port 11434

```bash
sudo ufw allow 11434/tcp
sudo ufw status
```

You should see:
```
11434/tcp                  ALLOW       Anywhere
```

### Test Again from Local Machine

```bash
curl http://your-vps-ip:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Say hello",
  "stream": false
}'
```

Should return JSON with the model's response.

---

## Container Management

### Useful Commands

```bash
# Check Ollama status
docker ps | grep ollama

# View Ollama logs
docker logs ollama -f

# Restart Ollama
docker restart ollama

# Stop Ollama
docker stop ollama

# Start Ollama
docker start ollama

# Remove Ollama (keeps volume/models)
docker rm -f ollama

# List downloaded models
docker exec ollama ollama list

# Delete a model
docker exec ollama ollama rm llama3:8b
```

### Update Ollama

```bash
# Pull latest Ollama image
docker pull ollama/ollama

# Recreate container (models persist in volume!)
docker rm -f ollama

docker run -d \
  --name ollama \
  --restart unless-stopped \
  -p 11434:11434 \
  -v ollama_models:/root/.ollama \
  ollama/ollama
```

---

## Volume Management

### Check Volume Size

```bash
docker volume inspect ollama_models
```

### Backup Models Volume

```bash
# Create backup
docker run --rm \
  -v ollama_models:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/ollama_models_backup.tar.gz /data

# Restore backup
docker run --rm \
  -v ollama_models:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/ollama_models_backup.tar.gz -C /
```

### Delete Volume (Removes All Models!)

```bash
# Stop and remove container first
docker rm -f ollama

# Delete volume
docker volume rm ollama_models
```

---

## Integration with n8n

Once Ollama is running:

1. Get your VPS IP: `curl ifconfig.me`
2. Update `.env` file:
   ```
   OLLAMA_API_URL=http://your-vps-ip:11434
   ```
3. In n8n Ollama node:
   - Base URL: `http://your-vps-ip:11434`
   - Model: `llama3:8b`

**If n8n is also in Docker on the same VPS:**

Use Docker networking instead of IP:

```bash
# Create shared network (if not exists)
docker network create app_network

# Reconnect both containers
docker network connect app_network ollama
docker network connect app_network n8n

# In n8n Ollama node, use:
# Base URL: http://ollama:11434
```

This allows n8n to reach Ollama via container name instead of IP.

---

## Monitoring Resources

### Check Container Resource Usage

```bash
docker stats ollama
```

Shows:
- CPU usage
- Memory usage (should be ~2-3GB with llama3:8b loaded)
- Network I/O

### Check VPS Memory

```bash
free -h
```

Ensure you have ~1GB free for OS overhead.

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs ollama

# Common issue: Port already in use
sudo lsof -i :11434

# If something else is using port:
sudo systemctl stop ollama  # If native Ollama installed
# Then restart Docker container
docker start ollama
```

### Can't Pull Models (Disk Full)

```bash
# Check disk space
df -h

# Check volume usage
docker system df -v

# Clean up unused Docker resources
docker system prune -a
```

### Out of Memory Errors

```bash
# Try smaller model
docker exec ollama ollama pull llama3.2:3b

# Or remove unused models
docker exec ollama ollama list
docker exec ollama ollama rm <unused-model>
```

### External Access Blocked

```bash
# Verify firewall
sudo ufw status | grep 11434

# Check Hostinger VPS firewall (in control panel)
# Ensure port 11434 is open there too

# Verify container is listening on all interfaces
docker inspect ollama | grep -A 5 "PortBindings"
```

---

## Docker Compose (Optional - Recommended)

For easier management, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - app_network

volumes:
  ollama_models:

networks:
  app_network:
    external: true
```

Then manage with:
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Update
docker-compose pull
docker-compose up -d
```

---

## Next Steps

After Ollama is running:
1. Test with `scripts/query.py` (when n8n workflow is ready)
2. Build n8n workflow
3. Launch Streamlit app
4. Record demo video

---

**Tutorial-ready tip:** This Docker setup makes great content - show viewers container management, volumes, and networking!
