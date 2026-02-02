#!/bin/bash
echo "================================"
echo "  Skyrama Private Server Setup  "
echo "================================"
echo

# Change to project root directory
cd "$(dirname "$0")/.."

if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed."
    echo "Please install Python 3.13+ using your package manager."
    exit 1
fi

echo "Python found!"
python3 --version
echo

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists."
fi

echo
echo "Activating virtual environment..."
source .venv/bin/activate

echo
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo
echo "================================"
echo "        Setup complete!         "
echo "================================"
echo
echo "You can now run ./scripts/start.sh to start the server."
echo
