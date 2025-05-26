#!/bin/bash
# OpenAI SDK Auto-Generator - Standalone Script
# Usage: wget https://your-domain.com/standalone_generator.sh | sh -s -- <JSON_URL>
# Example: wget https://your-domain.com/standalone_generator.sh | sh -s -- http://localhost:8000/openapi.json

set -e  # Exit on any error

# ========================
# CONFIGURATION PARAMETERS
# ========================
JSON_URL="$1"
CLIENT_OUTPUT_DIR="openai_sdk_client_output"
CLASS_NAME="GeneratedClient"
OUTPUT_FILE="generated_openai_sdk.py"
TEMP_DIR="openai_sdk_temp_$$"
SDK_AUTOGEN_FILE="sdk_autogen_temp.py"

# Validate input
if [ -z "$JSON_URL" ]; then
    echo "Error: JSON_URL is required"
    echo "Usage: $0 <JSON_URL>"
    echo "Example: $0 http://localhost:8000/openapi.json"
    exit 1
fi

echo "Starting OpenAI SDK generation from: $JSON_URL"

# Create temporary directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Function to cleanup
cleanup() {
    echo "Cleaning up temporary files..."
    cd ..
    rm -rf "$TEMP_DIR" 2>/dev/null || true
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# ========================
# CHECK DEPENDENCIES
# ========================
echo "Checking dependencies..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is required but not installed"
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

# Install required packages
echo "Installing required packages..."
$PIP_CMD install --user openapi-python-client requests 2>/dev/null || {
    echo "Warning: Could not install packages with --user flag, trying without..."
    $PIP_CMD install openapi-python-client requests || {
        echo "Error: Failed to install required packages"
        echo "Please ensure you have pip and proper permissions to install packages"
        exit 1
    }
}

# ========================
# DOWNLOAD SDK AUTOGEN SCRIPT
# ========================
FILE_REMOTE="https://github.com/anhvth/openai_sdk_autogen/blob/1964383620129fad3c9c40dbf932859f6ed4ef72/sdk_autogen.py"

echo "Downloading SDK autogen script from: $FILE_REMOTE"

# Convert GitHub blob URL to raw URL
RAW_URL=$(echo "$FILE_REMOTE" | sed 's|github.com|raw.githubusercontent.com|' | sed 's|/blob||')

# Download the SDK autogen script
if command -v wget &> /dev/null; then
    wget -q -O "$SDK_AUTOGEN_FILE" "$RAW_URL" || {
        echo "Error: Failed to download SDK autogen script with wget"
        exit 1
    }
elif command -v curl &> /dev/null; then
    curl -s -L -o "$SDK_AUTOGEN_FILE" "$RAW_URL" || {
        echo "Error: Failed to download SDK autogen script with curl"
        exit 1
    }
else
    echo "Error: Neither wget nor curl is available for downloading"
    exit 1
fi

# Verify the file was downloaded successfully
if [ ! -f "$SDK_AUTOGEN_FILE" ] || [ ! -s "$SDK_AUTOGEN_FILE" ]; then
    echo "Error: Failed to download or empty SDK autogen script"
    exit 1
fi

echo "SDK autogen script downloaded successfully"

# ========================
# GENERATE CLIENT
# ========================
echo "Generating OpenAPI client from $JSON_URL..."

# Clean up previous output
rm -rf "$CLIENT_OUTPUT_DIR" 2>/dev/null || true

# Generate client using openapi-python-client
python3 -m openapi_python_client generate \
    --url "$JSON_URL" \
    --meta=none \
    --output-path "$CLIENT_OUTPUT_DIR" \
    --overwrite || {
    echo "Error: Failed to generate OpenAPI client from $JSON_URL"
    echo "Please ensure the URL is accessible and returns valid OpenAPI JSON"
    exit 1
}

echo "OpenAPI client generated successfully"

# ========================
# GENERATE SDK WRAPPER
# ========================
echo "Generating SDK wrapper..."

python3 "$SDK_AUTOGEN_FILE" \
    --package "$CLIENT_OUTPUT_DIR" \
    --output "$OUTPUT_FILE" \
    --class-name "$CLASS_NAME" || {
    echo "Error: Failed to generate SDK wrapper"
    exit 1
}

# ========================
# MOVE OUTPUT TO PARENT
# ========================
echo "Moving generated files to parent directory..."

# Move the generated SDK to parent directory
mv "$OUTPUT_FILE" "../$OUTPUT_FILE" || {
    echo "Error: Failed to move output file"
    exit 1
}

# Optionally move the client directory as well
if [ -d "$CLIENT_OUTPUT_DIR" ]; then
    mv "$CLIENT_OUTPUT_DIR" "../$CLIENT_OUTPUT_DIR"
fi

# ========================
# CREATE USAGE EXAMPLE
# ========================

# Extract base URL from JSON_URL (remove /openapi.json or similar endpoints)
BASE_URL=$(echo "$JSON_URL" | sed 's|/openapi\.json.*$||' | sed 's|/docs.*$||' | sed 's|/redoc.*$||')

cat > "../example_usage.py" << EOF
#!/usr/bin/env python3
"""
Example usage of the generated SDK.
Generated from: $JSON_URL
"""

from generated_openai_sdk import $CLASS_NAME

# Initialize the client (using keyword arguments)
client = $CLASS_NAME(
    base_url="$BASE_URL"  # Extracted from your OpenAPI JSON URL
)

# Example usage (adjust based on your API)
try:
    # List available methods
    result = client.health_check()
    print(f"Health check result: {result}")
    
except Exception as e:
    print(f"Error using SDK: {e}")
    print("Make sure your API server is running and accessible!")
EOF

python3 -c "
print()
print('✅ Generation complete!')
print()
print('Generated files:')
print(f'  - $OUTPUT_FILE (main SDK file)')
print(f'  - $CLIENT_OUTPUT_DIR/ (OpenAPI client)')
print(f'  - example_usage.py (usage example)')
print()
print('To use the SDK:')
print(f'  from generated_openai_sdk import $CLASS_NAME')
print(f'  client = $CLASS_NAME(base_url=\"$BASE_URL\")')
print(f'  client.health_check()  # Example method call')
print()
"
