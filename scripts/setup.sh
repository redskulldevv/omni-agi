# scripts/setup.sh
#!/bin/bash

echo "Starting setup process..."

# Required tools
REQUIRED_TOOLS="python3 pip git"

# Check required tools
for tool in $REQUIRED_TOOLS; do
    if ! command -v $tool &> /dev/null; then
        echo "Error: $tool is required but not installed"
        exit 1
    fi
done

# Create project structure
mkdir -p src/{ai,blockchain,cognition,personality,models,utils}
mkdir -p config
mkdir -p logs
mkdir -p tests

# Create .env template if doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOF
# AI Configuration
CLAUDE_API_KEY=
GROQ_API_KEY=

# Blockchain Configuration
SOLANA_RPC_URL=
HELIUS_API_KEY=

# Social Media Configuration
TWITTER_API_KEY=
DISCORD_BOT_TOKEN=

# Database Configuration
REDIS_URL=

# Agent Configuration
AGENT_NAME=
LOG_LEVEL=INFO
EOF
    echo "Created .env template"
fi

# Create configuration files
if [ ! -f "config/settings.yaml" ]; then
    cat > config/settings.yaml << EOF
api:
  port: 8000
  host: "0.0.0.0"
  debug: false

ai:
  primary_model: "claude-3-opus"
  temperature: 0.7
  max_tokens: 1000

blockchain:
  network: "mainnet-beta"
  commitment: "confirmed"

logging:
  level: "INFO"
  file: "agent.log"
EOF
    echo "Created settings.yaml template"
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "Initialized git repository"
fi

# Create .gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# Project specific
config/*.yaml
!config/settings.yaml.example
EOF
    echo "Created .gitignore"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up pre-commit hooks
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
EOF
    echo "Created pre-commit configuration"
    pip install pre-commit
    pre-commit install
fi

echo "Running initial tests..."
python -m pytest tests/

echo "Setup complete!"
echo "Please update .env with your configuration values"
