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

# Check and activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    print_status "Activated virtual environment"
else
    print_error "Virtual environment not found. Run setup.sh first"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    print_error ".env file not found"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the agent
print_status "Starting AI Agent..."
python3 src/agent.py 2>&1 | tee -a logs/agent.log

# Keep script running and handle exit
cleanup() {
    print_status "Stopping AI Agent..."
    pkill -f "python3 src/agent.py"
    deactivate
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for agent process
wait
