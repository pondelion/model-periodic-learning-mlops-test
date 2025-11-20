"""
Generate dataset summary using either fixed logic or LLM-generated code.
"""

from typing import Any

import pandas as pd

from ..llm import get_llm
from ..models.summary import SummaryResult
from ..prompts.summary import SUMMARY_CODE_PROMPT
from ..utils.exceptions import CodeExecutionError
from ..utils.logger import get_logger
from .code_parser import extract_code_from_block

logger = get_logger(__name__)


def fixed_summary_logic(df) -> str:
    """
    A fallback fixed summary logic (used if not using LLM).

    Args:
        df: pandas DataFrame

    Returns:
        str summary
    """
    lines = [
        f"Rows: {len(df)}",
        "Columns:",
    ]

    for col in df.columns:
        lines.append(f"  {col}: {df[col].dtype}, missing={df[col].isna().sum()}")

    return "\n".join(lines)


def generate_summary_with_llm(
    df: pd.DataFrame,
    metadata_str: str = 'not available',
    summary_code_error: str = 'no error',
    training_code_error: str = 'no error',
    llm = None,
    debug: bool = False,
) -> SummaryResult:
    """
    Generate summary code via LLM and execute it.

    Args:
        df: pandas DataFrame
        metadata_str: str

    Returns:
        SummaryResult
    """

    if llm is None:
        llm = get_llm()

    prompt = SUMMARY_CODE_PROMPT.format(
        metadata=metadata_str,
        summary_code_error=summary_code_error,
        training_code_error=training_code_error,
    )

    llm_res = llm.invoke(prompt)
    if isinstance(llm_res, str):
        llm_res_str = llm_res
    elif hasattr(llm_res, 'content'):
        llm_res_str = llm_res.content
    else:
        raise RuntimeError(f'unsupported response format : {llm_res}')
    try:
        code = extract_code_from_block(llm_res_str)
    except ValueError as e:
        if debug:
            logger.info(f"llm_res_str : {llm_res_str}")
        raise e

    # logger.info("Generated summary code from LLM:\n%s", code)

    local_vars: dict[str, Any] = {"df": df}

    try:
        exec(code, {}, local_vars)
    except Exception as e:
        logger.error('Generated code with error : \n')
        if debug:
            logger.error(code)
        raise CodeExecutionError(f"Error executing summary code: {e}")  # noqa: B904

    summary_text = local_vars.get("summary_text")
    if summary_text is None:
        raise CodeExecutionError("summary_text variable not produced by LLM code.")

    return SummaryResult(summary_text=summary_text, summary_code=code)
