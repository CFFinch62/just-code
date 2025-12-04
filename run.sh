#!/bin/bash
# Just Code - Run Script
# Activates venv and runs the application

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate venv and run as module
source venv/bin/activate
python3 -m justcode.main
