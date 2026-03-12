#!/bin/bash
# Setup development environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

echo "==================================="
echo "PiSync Development Setup"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$PROJECT_ROOT/.venv/bin/activate"

# Install development dependencies
echo -e "${YELLOW}Installing development dependencies...${NC}"
pip install --upgrade pip wheel setuptools
pip install -e "$PROJECT_ROOT[dev,test,build]"

echo ""
echo -e "${GREEN}Development environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Run tests: pytest"
echo "3. Format code: make format"
echo "4. Run linting: make lint"
echo "5. Start development: make run"
