# LogicLens LLM Integration with Ollama

## Overview

LogicLens integrates with [Ollama](https://ollama.ai) to provide local LLM capabilities for analyzing logs, test results, and security data. The integration allows you to use various LLM models without sending data to external services.

## Requirements

- [Ollama](https://ollama.ai/download) installed and running
- A compatible LLM model (e.g., llama2, deepseek-coder:r1, etc.)

## Setup

### 1. Install Ollama

Follow the instructions on the [Ollama website](https://ollama.ai/download) to install Ollama for your operating system:

For macOS and Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

For Windows, download and run the installer from the website.

### 2. Pull a Model

Pull a model that you want to use with LogicLens:

```bash
# For general purpose analysis
ollama pull llama2

# For code-related analysis (recommended)
ollama pull deepseek-coder:r1

# For a smaller model (faster but less capable)
ollama pull deepseek-coder:r1-q4_K_M
```

### 3. Verify Available Models

```bash
ollama list
```

## Configuration

LogicLens provides several ways to configure the Ollama integration:

### Using the Management Script

The `logiclens_manage.py` script includes a dedicated `ollama` command to help configure and manage the Ollama integration:

```bash
# Show current Ollama configuration
python logiclens_manage.py ollama

# List available models
python logiclens_manage.py ollama --list-models

# Verify Ollama setup
python logiclens_manage.py ollama --verify

# Update Ollama configuration
python logiclens_manage.py ollama --ollama-host http://localhost:11434 --ollama-model deepseek-coder:r1
```

### Using the Environment File

You can also manually edit the `.env` file in the backend directory to update the Ollama configuration:

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:r1
```

### Using the Setup Helper

The `setup_env_file.py` script provides a convenient way to update the Ollama configuration:

```bash
# List available models
python setup_env_file.py --list-models

# Update Ollama configuration
python setup_env_file.py --host http://localhost:11434 --model deepseek-coder:r1
```

## Verification

When starting LogicLens with `logiclens_manage.py start`, the script will automatically verify the Ollama integration:

1. Check if Ollama is installed
2. Verify the Ollama service is running
3. Confirm the specified model is available

If any issues are detected, the script will attempt to recover (e.g., start the Ollama service or pull the required model) or provide helpful error messages.

## Error Recovery

The error recovery system in LogicLens can automatically handle common Ollama-related issues:

- `OLM_001`: Ollama server not running or unreachable
- `OLM_002`: Ollama model not found or not available
- `OLM_003`: Ollama request timeout
- `OLM_004`: Ollama API error
- `OLM_005`: Ollama installation issue

## Troubleshooting

If you encounter issues with the Ollama integration:

1. Verify Ollama is running:
   ```bash
   # Check if Ollama is running
   curl -s http://localhost:11434/api/tags
   ```

2. Check available models:
   ```bash
   ollama list
   ```

3. Make sure your model is pulled:
   ```bash
   ollama pull deepseek-coder:r1
   ```

4. Verify Ollama configuration:
   ```bash
   python logiclens_manage.py ollama --verify
   ```

5. If all else fails, restart Ollama:
   ```bash
   # Kill Ollama processes
   pkill ollama

   # Start Ollama again
   ollama serve
   ```