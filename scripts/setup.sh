#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Create virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing project dependencies..."
pip install -r requirements.txt

# Set up pre-commit hooks
print_status "Setting up pre-commit hooks..."
pre-commit install

# Create .env file from example
if [ ! -f .env ]; then
    cp .env.example .env
    print_status "Created .env file. Please update with your API keys."
fi

# Final setup message
echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${YELLOW}Don't forget to:${NC}"
echo "1. Update your .env file with your API keys"
echo "2. Configure your RPC endpoints"
echo "3. Set up your Discord bot"

# Activation reminder
echo -e "\n${GREEN}To activate your virtual environment:${NC}"
echo "source venv/bin/activate"
