"""
Utility for retry logic in LangGraph nodes.
"""

from collections.abc import Callable

from utils.logger import get_logger

logger = get_logger(__name__)


def retry(func: Callable, max_retry: int):
    """
    Execute a function with retry logic.

    Args:
        func: Callable
        max_retry: maximum retries

    Returns:
        Function return value

    Raises:
        Last exception
    """

    for attempt in range(1, max_retry + 1):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retry} failed: {e}")
            if attempt >= max_retry:
                raise
