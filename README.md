# OpenAI SDK Auto-Generator

Automatically generate OpenAI-style SDK clients from OpenAPI specifications. This tool creates clean, typed Python SDKs that follow OpenAI's client patterns and conventions.

## 🚀 Quick Start

The easiest way to use this tool is via the standalone script that requires no local setup:

```bash
# Generate SDK from any OpenAPI JSON URL
wget -O generator.sh https://raw.githubusercontent.com/anhvth/openai_sdk_autogen/refs/heads/main/standalone_generator.sh
sh generator.sh http://localhost:8000/openapi.json

# Or with curl
curl -o generator.sh https://raw.githubusercontent.com/anhvth/openai_sdk_autogen/refs/heads/main/standalone_generator.sh
sh generator.sh http://localhost:8000/openapi.json
```

This will automatically:
- Download and install dependencies
- Generate the OpenAPI client
- Create an OpenAI-style SDK wrapper
- Provide usage examples

## 📋 What Gets Generated

The tool generates:
- `generated_openai_sdk.py` - Main SDK file with OpenAI-style interface
- `openai_sdk_client_output/` - Raw OpenAPI client (optional)
- `example_usage.py` - Usage examples and documentation

Example generated SDK usage:
```python
from generated_openai_sdk import GeneratedClient

# Initialize with OpenAI-style patterns
client = GeneratedClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# Use generated methods
result = client.some_method(param1="value1", param2="value2")
```

## 🔧 Configuration

The standalone script uses these defaults:
- **Output file:** `generated_openai_sdk.py`
- **Class name:** `GeneratedClient`
- **Client directory:** `openai_sdk_client_output`

## 🌟 Features

### OpenAI-Style Interface
- **Familiar patterns:** Follows OpenAI client conventions
- **Authentication:** Built-in API key and Bearer token support
- **Type hints:** Full typing support with proper annotations
- **Error handling:** Consistent error patterns

### Smart Code Generation
- **Method wrapping:** Auto-wraps all client methods
- **Parameter forwarding:** Preserves original signatures and defaults
- **Import management:** Handles complex type imports automatically
- **Documentation:** Generates docstrings and usage examples

### Flexible Deployment
- **Standalone:** No local setup required, works with wget/curl
- **Cross-platform:** Works on macOS, Linux, and WSL

## 📖 Examples

### Basic Usage
```python
from generated_openai_sdk import GeneratedClient

client = GeneratedClient(base_url="https://api.example.com")
result = client.list_items()
```

### With Authentication
```python
client = GeneratedClient(
    base_url="https://api.example.com",
    api_key="sk-1234567890abcdef"
)
```

### Custom Headers
```python
client = GeneratedClient(
    base_url="https://api.example.com",
    headers={"Custom-Header": "value"}
)
```

## 🐛 Troubleshooting

### Common Issues

**"Failed to download SDK autogen script"**
- Check internet connection
- Verify GitHub URL is accessible
- Try using curl instead of wget

**"Failed to generate OpenAPI client"**
- Verify the OpenAPI JSON URL is accessible
- Check that the JSON is valid OpenAPI 3.0+ format
- Ensure the API server is running

**"Failed to install required packages"**
- Try running with `sudo` if permissions are needed
- Use virtual environment: `python -m venv venv && source venv/bin/activate`
- Install manually: `pip install openapi-python-client requests`

### Debug Mode

For verbose output, edit the scripts to remove `-q` and `-s` flags from wget/curl commands.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **GitHub Repository:** https://github.com/anhvth/openai_sdk_autogen
- **Standalone Script:** https://raw.githubusercontent.com/anhvth/openai_sdk_autogen/refs/heads/main/standalone_generator.sh
- **Issues:** https://github.com/anhvth/openai_sdk_autogen/issues

---

**Made with ❤️ for developers who love clean APIs**
