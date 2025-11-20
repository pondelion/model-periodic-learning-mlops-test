"""
Helper utilities for file operations.
"""

import os
import pickle
from typing import Any


def ensure_dir(path: str) -> None:
    """
    Ensure directory exists; create if missing.

    Args:
        path: Directory path.
    """
    os.makedirs(path, exist_ok=True)


def save_pickle(obj: Any, file_path: str) -> None:
    """
    Save an object to a pickle file.

    Args:
        obj: Python object.
        file_path: Destination path.
    """
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)
