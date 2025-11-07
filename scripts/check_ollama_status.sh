#!/bin/bash
# Quick Ollama VPS Health Check & Model Status

VPS_HOST="root@158.220.127.4"

echo "=== Ollama VPS Health Check ==="
echo ""

# Check VPS resources
echo "1. VPS Resources:"
ssh $VPS_HOST "echo '   CPU:' && nproc && echo '   RAM:' && free -h | grep Mem | awk '{print \"   Total: \"\$2\" | Used: \"\$3\" | Free: \"\$4}'"
echo ""

# Check if Ollama is running
echo "2. Ollama Service Status:"
ssh $VPS_HOST "systemctl is-active ollama 2>/dev/null || echo '   Not running as service (might be in Docker)'"
echo ""

# Check available models
echo "3. Installed Models:"
ssh $VPS_HOST "ollama list" | awk '{print "   "$0}'
echo ""

# Check if any model is currently loaded in memory
echo "4. Current Memory Usage:"
ssh $VPS_HOST "ps aux | grep ollama | grep -v grep | head -1" | awk '{print "   "$0}'
echo ""

# Quick speed test with smallest model
echo "5. Quick Speed Test (llama3.2:3b if available):"
echo "   Testing cold start..."
ssh $VPS_HOST "time ollama run llama3.2:3b 'Hi' 2>&1" | grep real
echo ""

echo "=== Recommendations ==="

# Check if models are too large
TOTAL_RAM=$(ssh $VPS_HOST "free -g | grep Mem | awk '{print \$2}'")
echo "   Total RAM: ${TOTAL_RAM}GB"

if [ "$TOTAL_RAM" -lt 8 ]; then
    echo "   ⚠️  Warning: Less than 8GB RAM detected"
    echo "   Recommended: Use 3B models (llama3.2:3b, phi3:mini)"
else
    echo "   ✓ RAM sufficient for 7-8B models"
fi

echo ""
echo "=== Done ==="
