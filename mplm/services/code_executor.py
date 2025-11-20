"""
Generic safe exec wrapper (currently unused but available).
"""

from typing import Any

from ..utils.exceptions import CodeExecutionError


def safe_exec(code: str, globals_: dict[str, Any], locals_: dict[str, Any]):
    """
    Execute Python code safely with controlled namespaces.

    Raises:
        CodeExecutionError
    """
    try:
        exec(code, globals_, locals_)
    except Exception as err:
        raise CodeExecutionError(f"Execution failed: {err}") from err
        # import traceback
        # tb_str = traceback.format_exc()
        # raise CodeExecutionError(f"Execution failed ({type(err).__name__}): {err}\n{tb_str}") from err
