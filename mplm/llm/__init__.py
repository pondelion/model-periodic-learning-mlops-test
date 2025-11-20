"""
LLM package initializer.
Exposes get_llm() for global usage.
"""

from .client import get_llm

__all__ = ["get_llm"]
