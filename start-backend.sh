#!/bin/bash

# Start Backend Server
# This script starts the FastAPI backend on port 8000

echo "🚀 Starting Backend Server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📚 API Docs will be available at: http://localhost:8000/docs"
echo ""

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "✅ Starting server..."
echo "   Press Ctrl+C to stop"
echo ""
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

