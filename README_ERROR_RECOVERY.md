# LogicLens Error Recovery System

## Overview

The LogicLens Error Recovery System provides robust error handling, diagnostics, and automatic recovery mechanisms for the LogicLens application. It is designed to handle common failure scenarios gracefully, provide detailed diagnostics, and help users troubleshoot issues.

## Key Features

- **Standardized Error Codes**: Categorized error codes (ENV_*, DEP_*, PRC_*, etc.) for clear error identification
- **Automatic Recovery**: Built-in recovery mechanisms for common errors:
  - Virtual environment creation failures
  - Package installation issues
  - Port conflicts
  - Flask application startup problems
- **Detailed System Diagnostics**: Extensive system information logged at startup and when errors occur
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Integration with LogicLens Manager

The error recovery system is integrated with the `logiclens_manage.py` script, which now provides:

1. Detailed error reporting with error codes
2. Automatic recovery attempts when possible
3. System diagnostics to assist troubleshooting
4. Graceful degradation when recovery isn't possible

## Usage

The error recovery system is automatically used when you run the `logiclens_manage.py` script:

```
python logiclens_manage.py start
```

When an error occurs, you'll see detailed error information including:
- Error code and description
- System diagnostic information
- Recovery attempts and results

## Common Error Codes

| Code    | Description                        | Recovery Action                           |
|---------|------------------------------------|--------------------------------------------|
| ENV_001 | Python version incompatible        | Searches for compatible Python version    |
| ENV_002 | Virtual environment creation failed| Tries alternative creation method         |
| DEP_001 | Pip not found in virtual environment | Recreates virtual environment           |
| DEP_002 | Dependency installation failed     | Retries with different options            |
| PRC_001 | Port already in use                | Finds and terminates process or uses alt port |
| APP_001 | Flask application failed to start  | Diagnoses and tries with different settings |

## Standalone Usage

You can also use the error recovery system in your own scripts:

```python
from error_recovery import ErrorHandler, LogicLensError

# Initialize the handler with your configuration
config = {
    "backend_dir": "backend",
    "venv_dir": "venv",
    "flask_port": 5050,
    # other config options...
}

# Create error handler with your logging function
handler = ErrorHandler(config, your_log_function)

try:
    # Your code here
    pass
except Exception as e:
    # Handle the error
    error = LogicLensError("ENV_001", str(e), e)
    if handler.handle_error(error, context="My operation"):
        print("Recovery successful!")
    else:
        print("Recovery failed")
```

## Extending the System

To add new recovery mechanisms:
1. Add a new error code to the `ERROR_CODES` dictionary in `error_recovery.py`
2. Implement a recovery method following the naming pattern `_recover_XXX_YYY` where XXX_YYY is your error code in lowercase 