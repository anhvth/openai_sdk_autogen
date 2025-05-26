#!/bin/bash

# prerequisites: start a local server that serves the OpenAPI JSON file at http://localhost:8000/openapi.json
# Usage: ./run.sh [URL]


FILE_REMOTE=https://github.com/anhvth/openai_sdk_autogen/blob/1964383620129fad3c9c40dbf932859f6ed4ef72/sdk_autogen.py

# ========================
# CONFIGURATION PARAMETERS
# ========================
CLIENT_OUTPUT_DIR="client_output"
CLASS_NAME="HelloWorldClient"
SERVER_PORT=8000
SERVER_SCRIPT="src/example_server.py"
OUTPUT_FILE="generated_openai_sdk.py"
WAIT_TIME=3
JSON_URL=${1:-http://localhost:${SERVER_PORT}/openapi.json}

# Clean up previous output
rm -r "$CLIENT_OUTPUT_DIR" 2>/dev/null

# Start server in background and store PID
python "$SERVER_SCRIPT" --port "$SERVER_PORT" &
SERVER_PID=$!

# Function to cleanup server
cleanup() {
    echo "Stopping server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for server to start
echo "Waiting for server to start..."
sleep "$WAIT_TIME"

# Generate client
echo "Generating client from $JSON_URL..."
# Clear any environment variables that might interfere
unset MetaType
openapi-python-client generate --url "$JSON_URL" --meta=none --output-path "$CLIENT_OUTPUT_DIR" --overwrite

echo "Generation complete. Server will be stopped."

python sdk_autogen.py --package "$CLIENT_OUTPUT_DIR" \
       --output "$OUTPUT_FILE" \
       --class-name "$CLASS_NAME"     # optional



python test.py
