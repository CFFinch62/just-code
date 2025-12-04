#!/bin/bash
# Build script for macOS
# Creates an app bundle in dist/JustCode.app/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "Building Just Code for macOS"
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

# Post-build for macOS
if [ -d "dist/JustCode.app" ]; then
    echo ""
    echo "Build successful!"
    echo "App bundle: dist/JustCode.app"
    echo "Run with: open dist/JustCode.app"
    echo ""
    echo "To create a DMG for distribution:"
    echo "  hdiutil create -volname JustCode -srcfolder dist/JustCode.app -ov dist/JustCode.dmg"
fi

