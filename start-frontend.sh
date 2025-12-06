#!/bin/bash

# Start Frontend Server
# This script starts the Next.js frontend on port 3000

echo "🚀 Starting Frontend Server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo ""

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies (this may take a minute)..."
    npm install
    echo "✅ Dependencies installed"
fi

# Start the development server
echo ""
echo "✅ Starting development server..."
echo "   Press Ctrl+C to stop"
echo ""
npm run dev

