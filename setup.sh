#!/bin/bash
# Just Code - Setup Script
# Creates virtual environment and installs dependencies

set -e

echo "Setting up Just Code development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run Just Code:"
echo "  source venv/bin/activate"
echo "  python justcode/main.py"
echo ""
echo "Or use the run script:"
echo "  ./run.sh"
