#!/bin/bash
# Build and distribution script for PiSync

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

echo "==================================="
echo "PiSync Build and Distribution"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clean previous builds
echo -e "${YELLOW}[1/5] Cleaning previous builds...${NC}"
rm -rf "$BUILD_DIR" "$DIST_DIR" "$PROJECT_ROOT"/*.egg-info
find "$PROJECT_ROOT" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Install build dependencies
echo -e "${YELLOW}[2/5] Installing build dependencies...${NC}"
pip install --upgrade build twine

# Build wheel and source distributions
echo -e "${YELLOW}[3/5] Building distributions...${NC}"
cd "$PROJECT_ROOT"
python -m build

# Verify distributions
echo -e "${YELLOW}[4/5] Verifying distributions...${NC}"
twine check "$DIST_DIR"/*

# Summary
echo -e "${YELLOW}[5/5] Build complete!${NC}"
echo ""
echo -e "${GREEN}Distribution files created:${NC}"
ls -lh "$DIST_DIR"
echo ""
echo "To publish to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "To publish to TestPyPI:"
echo "  twine upload --repository testpypi dist/*"
