#!/bin/bash
# CV-RAG VPS Setup Script
# Run this script on your VPS to set up the project directory

set -e  # Exit on error

echo "======================================"
echo "  CV-RAG VPS Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a regular user.${NC}"
fi

# Create project directory
PROJECT_DIR="/cv-rag"
echo -e "${GREEN}Creating project directory: $PROJECT_DIR${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Directory $PROJECT_DIR already exists.${NC}"
    read -p "Do you want to remove it and start fresh? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$PROJECT_DIR"
        echo "Removed existing directory."
    else
        echo "Keeping existing directory. Exiting."
        exit 1
    fi
fi

# Create directory and set permissions
sudo mkdir -p "$PROJECT_DIR"
sudo chown $USER:$USER "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo ""
echo -e "${GREEN}✓ Project directory created${NC}"
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git is not installed. Installing...${NC}"
    sudo apt update
    sudo apt install -y git
fi

# Clone repository or provide instructions
echo ""
echo "Next steps:"
echo "1. Clone your repository into $PROJECT_DIR:"
echo "   cd $PROJECT_DIR"
echo "   git clone https://github.com/yourusername/cv-rag.git ."
echo ""
echo "   OR manually copy files from your local machine:"
echo "   rsync -avz --exclude '.git' --exclude '.venv' --exclude '__pycache__' \\"
echo "     ~/Code/Projects/cv-rag/ user@your-vps-ip:$PROJECT_DIR/"
echo ""
echo "2. Copy and configure environment variables:"
echo "   cd $PROJECT_DIR"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Start Docker services:"
echo "   docker-compose up -d"
echo ""

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker is not installed${NC}"
    echo ""
    read -p "Do you want to install Docker now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        echo -e "${GREEN}✓ Docker installed${NC}"
        echo -e "${YELLOW}! You need to log out and back in for group changes to take effect${NC}"
    fi
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker Compose is not installed${NC}"
    echo ""
    read -p "Do you want to install Docker Compose now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Docker Compose..."
        sudo apt update
        sudo apt install -y docker-compose
        echo -e "${GREEN}✓ Docker Compose installed${NC}"
    fi
fi

echo ""
echo -e "${GREEN}======================================"
echo "  Setup Complete!"
echo "======================================${NC}"
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""
