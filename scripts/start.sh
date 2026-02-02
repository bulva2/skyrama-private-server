#!/bin/bash
echo "Starting Skyrama Private Server with FastAPI and Uvicorn..."

# Change to project root directory
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please run ./scripts/setup.sh first."
    exit 1
fi

uvicorn server:app --host 0.0.0.0 --port 3800 --reload
