#!/bin/bash
# Start script for the FastAPI server with uvicorn

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables
set -a
source .env
set +a

# Start the server with uvicorn
echo "Starting Liao Fan Si Xun proxy server..."
echo "Server will be available at http://localhost:${PORT:-8000}"
echo "Press Ctrl+C to stop"
echo ""

# Run with uvicorn directly for better control
# Check if we should use dashscope version
if [ -f "app_dashscope.py" ] && [ -n "$DASHSCOPE_API_KEY" ]; then
    echo "Using DashScope API integration..."
    uvicorn app_dashscope:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level info
else
    uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level info
fi