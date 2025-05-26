#!/bin/bash
# Test script for the standalone generator

# Test with your local server
echo "Testing standalone generator with local server..."

# Start the example server in background
cd /Users/anhvth/projects/openai-sdk-autogen
python src/example_server.py --port 8000 &
SERVER_PID=$!

# Function to cleanup server
cleanup() {
    echo "Stopping test server..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

# Test the standalone generator
echo "Running standalone generator..."
./standalone_generator.sh http://localhost:8000/openapi.json

echo "Test completed!"
