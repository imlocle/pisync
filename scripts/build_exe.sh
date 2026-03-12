#!/bin/bash
# Build standalone executable using PyInstaller

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
DIST_DIR="$PROJECT_ROOT/dist/standalone"

echo "==================================="
echo "PiSync PyInstaller Build"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PyInstaller is installed
echo -e "${YELLOW}Checking for PyInstaller...${NC}"
if ! pip show pyinstaller > /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build executable
echo -e "${YELLOW}Building standalone executable...${NC}"
cd "$PROJECT_ROOT"

pyinstaller \
    --name=pisync \
    --onefile \
    --windowed \
    --icon=assets/icons/pisync_logo.png \
    --add-data="assets:assets" \
    --add-data="docs:docs" \
    --hidden-import=paramiko \
    --hidden-import=pydantic \
    --hidden-import=watchdog \
    --hidden-import=PySide6 \
    main.py

echo ""
echo -e "${GREEN}Build complete!${NC}"
echo "Executable location: $PROJECT_ROOT/dist/pisync"
