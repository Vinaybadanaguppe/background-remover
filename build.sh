#!/bin/sh

# Exit on error and print commands
set -ex

echo "Starting build process..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Ensure we're using Python 3
if ! command -v python3 > /dev/null 2>&1; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Print Python version
echo "Using Python version:"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
. venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# List installed packages
echo "Installed packages:"
pip list

echo "Build completed successfully!"
