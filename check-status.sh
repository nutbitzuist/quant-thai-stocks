#!/bin/bash

# Check if servers are running

echo "🔍 Checking server status..."
echo ""

# Check backend
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
    echo "   Health: http://localhost:8000/health"
    # Try to get actual status
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   Status: Healthy ✓"
    else
        echo "   Status: Port in use but not responding"
    fi
else
    echo "❌ Backend is NOT running"
    echo "   Start with: ./start-backend.sh"
fi

echo ""

# Check frontend
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Frontend is running on port 3000"
    echo "   URL: http://localhost:3000"
else
    echo "❌ Frontend is NOT running"
    echo "   Start with: ./start-frontend.sh"
fi

echo ""
echo "💡 To start both servers: ./start-all.sh"

