#!/bin/bash
# Stop script for the FastAPI server

echo "Stopping Liao Fan Si Xun proxy server..."

# Find and kill uvicorn processes
pkill -f "uvicorn app:app"

echo "Server stopped."