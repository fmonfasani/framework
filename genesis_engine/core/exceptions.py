"""Genesis Engine exceptions"""

class GenesisException(Exception):
    """Base exception for Genesis Engine"""
    pass

class ProjectCreationError(GenesisException):
    """Error during project creation"""
    pass

class ValidationError(GenesisException):
    """Validation error"""
    pass