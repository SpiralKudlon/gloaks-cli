#!/bin/bash
set -e

echo "Installing Gloaks-CLI..."

# Check python version
python3 --version

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install .

echo "Installation complete!"
echo "Run 'gloaks --help' to get started."
