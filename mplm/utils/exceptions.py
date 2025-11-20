"""
Custom exception types used across the system.
"""


class LLMConfigError(Exception):
    """Raised when LLM configuration is missing or invalid."""
    pass


class CodeExecutionError(Exception):
    """Raised when executing LLM-generated code fails."""
    pass
