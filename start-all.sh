#!/bin/bash

# Start Both Backend and Frontend Servers
# This script starts both servers in separate terminal windows/tabs

echo "🚀 Starting Quant Stock Analysis Platform..."
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to check if a port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
    return $?
}

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend may already be running."
    echo "   Check: http://localhost:8000/health"
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend may already be running."
    echo "   Check: http://localhost:3000"
fi

echo ""
echo "Starting servers..."
echo ""

# Detect OS and open terminals accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript to open new terminal windows
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ./start-backend.sh\""
    sleep 2
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ./start-frontend.sh\""
    echo "✅ Servers starting in separate Terminal windows"
    echo ""
    echo "📍 Backend:  http://localhost:8000"
    echo "📍 Frontend: http://localhost:3000"
    echo ""
    echo "💡 Tip: Keep both terminal windows open while using the app"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - try to use gnome-terminal or xterm
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && ./start-backend.sh; exec bash"
        sleep 2
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && ./start-frontend.sh; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$SCRIPT_DIR' && ./start-backend.sh" &
        sleep 2
        xterm -e "cd '$SCRIPT_DIR' && ./start-frontend.sh" &
    else
        echo "⚠️  Could not detect terminal. Please run manually:"
        echo "   Terminal 1: ./start-backend.sh"
        echo "   Terminal 2: ./start-frontend.sh"
        exit 1
    fi
    echo "✅ Servers starting in separate terminal windows"
else
    echo "⚠️  Unsupported OS. Please run manually:"
    echo "   Terminal 1: ./start-backend.sh"
    echo "   Terminal 2: ./start-frontend.sh"
    exit 1
fi

echo ""
echo "⏳ Wait 10-15 seconds for servers to start, then open:"
echo "   http://localhost:3000"

