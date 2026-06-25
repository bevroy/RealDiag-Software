#!/bin/bash
# Installation script for RealDiag-Software on Linux/macOS

set -e

echo "======================================"
echo "RealDiag-Software Installation"
echo "======================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Check Python version (need 3.7+)
MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 7 ]); then
    echo "Error: Python 3.7 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "Python version check passed"
echo ""

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? (recommended) [Y/n] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Virtual environment created and activated"
else
    echo "Skipping virtual environment creation"
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "To run RealDiag:"
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "  1. Activate the virtual environment: source venv/bin/activate"
    fi
    echo "  2. Run: python main.py --help"
    echo ""
    echo "For Docker deployment:"
    echo "  docker compose up --build"
    echo ""
else
    echo "Error: Installation failed"
    exit 1
fi
