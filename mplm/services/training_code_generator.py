"""
Generate ML training/evaluation code using LLM.
"""

from ..llm import get_llm
from ..prompts.train_code import FIX_ERROR_CODE_PROMPT, TRAIN_CODE_PROMPT
from ..utils.logger import get_logger
from .code_parser import extract_code_from_block

logger = get_logger(__name__)


def generate_training_code(
    dataset_summary: str,
    target_column: str,
    seed: int = 42,
    training_code_error: str = 'no error',
    llm = None,
) -> str:
    """
    Generate Python code for training and evaluation of an ML model using LLM.

    Args:
        dataset_summary: Dataset summary string
        target_column: Name of the target variable
        seed: Random seed for splitting

    Returns:
        str: Python code string (wrapped in a python markdown block)
    """

    if llm is None:
        llm = get_llm()

    prompt = TRAIN_CODE_PROMPT.format(
        dataset_summary=dataset_summary,
        target_column=target_column,
        training_code_error=training_code_error,
    )

    llm_res = llm.invoke(prompt)
    if isinstance(llm_res, str):
        llm_res_str = llm_res
    elif hasattr(llm_res, 'content'):
        llm_res_str = llm_res.content
    else:
        raise RuntimeError(f'unsupported response format : {llm_res}')

    code = extract_code_from_block(llm_res_str)

    # logger.info("Generated training code:\n%s", code)

    return code


def generate_error_fixed_training_code(
    previous_code: str,
    previous_error: str,
    target_column: str,
    seed: int = 42,
    llm=None,
) -> str:
    """
    Generate Python code that fixes errors in previous training code using LLM.

    Args:
        previous_code: The Python code string that previously failed.
        previous_error: The error message produced by executing previous_code.
        target_column: Name of the target variable.
        seed: Random seed for reproducibility (optional).
        llm: Optional LLM client instance.

    Returns:
        str: Fixed Python code string (wrapped in a python markdown block)
    """

    if llm is None:
        llm = get_llm()

    prompt = FIX_ERROR_CODE_PROMPT.format(
        previous_code=previous_code,
        previous_error=previous_error,
        target_column=target_column,
    )

    llm_res = llm.invoke(prompt)
    if isinstance(llm_res, str):
        llm_res_str = llm_res
    elif hasattr(llm_res, "content"):
        llm_res_str = llm_res.content
    else:
        raise RuntimeError(f"unsupported response format: {llm_res}")

    fixed_code = extract_code_from_block(llm_res_str)

    return fixed_code
