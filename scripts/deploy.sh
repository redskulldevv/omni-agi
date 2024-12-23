#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
print_status "Activated virtual environment"

# Check if .env exists
if [ ! -f .env ]; then
    print_error ".env file not found"
    exit 1
fi

# Check if required API keys are set
source .env
REQUIRED_KEYS=(
    "CLAUDE_API_KEY"
    "GROQ_API_KEY"
    "SOLANA_RPC_URL"
    "ETH_RPC_URL"
    "DISCORD_TOKEN"
    "TWITTER_API_KEY"
)

for key in "${REQUIRED_KEYS[@]}"; do
    if [ -z "${!key}" ]; then
        print_error "$key is not set in .env"
        exit 1
    fi
done

# Install production dependencies if needed
pip install -r requirements.txt
print_status "Dependencies installed"

# Start the agent with PM2
if ! command -v pm2 &> /dev/null; then
    print_warning "PM2 not found. Installing..."
    npm install -g pm2
fi

print_status "Starting agent with PM2..."
pm2 start src/agent.py --name ai-agent --interpreter python3 \
    --max-memory-restart 1G \
    --time \
    --log logs/agent.log

# Enable startup script
pm2 startup
pm2 save

print_status "Agent deployed successfully!"
print_warning "Monitor logs with: pm2 logs ai-agent"
echo -e "\nUseful PM2 commands:"
echo "- Stop agent: pm2 stop ai-agent"
echo "- Restart agent: pm2 restart ai-agent"
echo "- View status: pm2 status"
echo "- View logs: pm2 logs ai-agent"
