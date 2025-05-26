# OpenAI SDK Auto-Generator

Automatically generate OpenAI-style SDK clients from OpenAPI specifications.

## Quick Start

### 1. Start your server and ensure OpenAPI JSON is accessible
```bash
# Make sure your API server is running and OpenAPI JSON is available
curl http://localhost:8000/openapi.json  # Verify it's accessible
```

### 2. Generate the SDK
```bash
wget -O generator.sh https://raw.githubusercontent.com/anhvth/openai_sdk_autogen/refs/heads/main/standalone_generator.sh
sh generator.sh http://localhost:8000/openapi.json
```

### 3. Use the generated SDK
```python
from generated_openai_sdk import GeneratedClient

client = GeneratedClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

result = client.some_method(param1="value1", param2="value2")
```

That's it! The tool generates `generated_openai_sdk.py` with OpenAI-style interface patterns.
