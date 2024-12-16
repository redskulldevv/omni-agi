# scripts/deploy.sh
#!/bin/bash

echo "Starting deployment process..."

# Environment variables
ENV_FILE=".env"
CONFIG_DIR="config"
LOGS_DIR="logs"

# Ensure required directories exist
mkdir -p $LOGS_DIR

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found"
    echo "Please create .env file with required configuration"
    exit 1
fi

# Load environment variables
source $ENV_FILE

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking configuration files..."
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Error: Config directory not found"
    exit 1
fi

echo "Initializing agent..."
python -m omni_agi.src.main initialize

echo "Starting agent services..."
python -m omni_agi.src.main start

echo "Deployment complete!"
