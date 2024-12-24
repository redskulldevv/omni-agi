# src/utils/errors.py
class BaseError(Exception):
    """Base error class for the application"""
    pass

class SecurityError(BaseError):
    """Security related errors"""
    pass

class ConfigError(BaseError):
    """Configuration related errors"""
    pass

class AgentError(BaseError):
    """Agent related errors"""
    pass