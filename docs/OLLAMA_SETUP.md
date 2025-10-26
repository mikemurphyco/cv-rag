# Ollama Installation Guide for Hostinger VPS

This guide will walk you through installing Ollama on your Hostinger VPS (KVM2 with 8GB RAM).

## Prerequisites

- Hostinger VPS (KVM2: 8GB RAM, 2 vCPU recommended)
- SSH access to your VPS
- Ubuntu OS (check version with `lsb_release -a`)

## Installation Steps

### 1. Connect to Your VPS

```bash
ssh root@your-vps-ip
# Or use the username you configured
```

### 2. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Ollama

Ollama provides an official installation script:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This script will:
- Download the Ollama binary
- Set up systemd service
- Start Ollama automatically

### 4. Verify Installation

Check that Ollama is running:

```bash
systemctl status ollama
```

You should see `active (running)` in green.

### 5. Pull Your First Model

For CV-RAG, we recommend **llama3:8b** (with 8GB RAM, you can comfortably run this):

```bash
ollama pull llama3:8b
```

This will download ~4.7GB. Wait for it to complete.

**Alternative models for testing:**
- `llama3.2:3b` - Smaller, faster (2GB)
- `qwen2.5:7b` - Good alternative to Llama

### 6. Test Ollama

Run a quick test:

```bash
ollama run llama3:8b "Tell me about retrieval augmented generation"
```

If you get a response, Ollama is working! Press `Ctrl+D` to exit.

### 7. Enable External Access (for n8n)

By default, Ollama only listens on localhost. To allow n8n to connect:

**Option A: Environment Variable (Recommended)**

Edit the Ollama service:

```bash
sudo systemctl edit ollama
```

Add these lines in the editor that opens:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter` in nano).

**Option B: Using systemd override**

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Add:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Save and exit.

**Reload and restart:**

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 8. Configure Firewall

Add firewall rule for Ollama (port 11434):

```bash
sudo ufw allow 11434/tcp
sudo ufw status
```

### 9. Test External Access

From your local machine:

```bash
curl http://your-vps-ip:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Say hello",
  "stream": false
}'
```

You should get a JSON response with the model's output.

## Resource Monitoring

Monitor Ollama's resource usage:

```bash
# Check memory usage
free -h

# Monitor Ollama process
htop  # Press F4 and search for "ollama"

# Check Ollama logs
journalctl -u ollama -f
```

## Useful Commands

```bash
# List downloaded models
ollama list

# Remove a model
ollama rm llama3:8b

# Check Ollama version
ollama --version

# Stop Ollama service
sudo systemctl stop ollama

# Start Ollama service
sudo systemctl start ollama

# Restart Ollama service
sudo systemctl restart ollama
```

## Troubleshooting

### Ollama won't start
```bash
# Check logs for errors
sudo journalctl -u ollama -n 50

# Check if port is in use
sudo lsof -i :11434
```

### Out of memory errors
- Try a smaller model: `ollama pull llama3.2:3b`
- Stop other services temporarily
- Upgrade to larger VPS

### Can't connect externally
- Verify firewall rules: `sudo ufw status`
- Check Ollama is bound to 0.0.0.0: `sudo netstat -tulpn | grep 11434`
- Ensure VPS provider firewall allows port 11434

## For n8n Integration

Once Ollama is running:

1. Get your VPS IP address: `curl ifconfig.me`
2. Update your `.env` file:
   ```
   OLLAMA_API_URL=http://your-vps-ip:11434
   ```
3. In n8n, use the Ollama node with:
   - Base URL: `http://your-vps-ip:11434`
   - Model: `llama3:8b`

## Security Notes

- Consider using a reverse proxy (nginx) with SSL for production
- Restrict port 11434 to specific IPs if possible
- Monitor resource usage regularly
- Keep Ollama updated: `curl -fsSL https://ollama.com/install.sh | sh`

## Next Steps

After Ollama is running:
1. Set up Neon Postgres database
2. Run chunker.py and embedder.py
3. Build n8n workflow
4. Test with query.py
5. Launch Streamlit app

---

**Tutorial-ready tip:** Screen record this installation process for your YouTube channel!
