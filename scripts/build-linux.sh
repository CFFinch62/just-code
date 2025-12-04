#!/bin/bash
# Build script for Linux
# Creates an executable in dist/JustCode/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "Building Just Code for Linux"
echo "=========================================="

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install PyInstaller if not present
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build
echo "Building..."
python build.py "$@"

# Make executable
if [ -f "dist/JustCode/JustCode" ]; then
    chmod +x dist/JustCode/JustCode
    echo ""
    echo "Build successful!"
    echo "Run with: ./dist/JustCode/JustCode"
fi

