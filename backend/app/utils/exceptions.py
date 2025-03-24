class OllamaError(Exception):
    """Base exception for OLLAMA-related errors"""
    pass

class OllamaConnectionError(OllamaError):
    """Raised when there are connection issues with OLLAMA"""
    pass

class OllamaModelError(OllamaError):
    """Raised when there are issues with the OLLAMA model"""
    pass

class OllamaTimeoutError(OllamaError):
    """Raised when OLLAMA request times out"""
    pass

class OllamaValidationError(OllamaError):
    """Raised when there are validation issues with the request"""
    pass 