"""
LangGraph node: generate summary.
"""

from ..models.state import WorkflowState
from ..services.summary_generator import fixed_summary_logic, generate_summary_with_llm
from ..utils.logger import get_logger

logger = get_logger(__name__)


def summary_chain(state: WorkflowState) -> WorkflowState:
    """
    LangGraph node for generating a dataset summary using LLM.

    This node attempts to generate a summary of the dataset using the
    generate_summary_with_llm service. It updates the WorkflowState
    with the summary result, status, and any encountered errors.

    Requires the state to have:
        - 'df': the dataset
        - optionally 'metadata': dataset metadata
        - 'summary_errors': list of previous summary errors
        - 'training_errors': list of previous training errors
        - optional 'llm': LLM client instance

    Behavior:
        - On success:
            - state["summary_result"] is updated with the generated summary
            - state["status"] is set to "ok"
            - state["summary_errors"] is cleared
        - On failure:
            - state["status"] is set to "failed"
            - the exception message is appended to state["summary_errors"]
            - state["retry_count"] is incremented
    """
    state.setdefault("summary_errors", [])
    state.setdefault("training_errors", [])

    df = state["df"]
    metadata = "not available"  # state["metadata"]

    logger.info("Running summary chain...")

    # Generate summary
    try:
        if len(state["summary_errors"]) > 0:
            summary_errors_str = '\n'.join(state["summary_errors"])
        else:
            summary_errors_str = 'no error'
        if len(state["training_errors"]) > 0:
            training_errors_str = '\n'.join(state["training_errors"])
        else:
            training_errors_str = 'no error'
        if state.get("use_fixed_summary", False):
            summary_result = fixed_summary_logic
        else:
            summary_result = generate_summary_with_llm(
                df,
                metadata_str=metadata,
                summary_code_error=summary_errors_str,
                training_code_error=training_errors_str,
                llm=state.get('llm', None),
            )
        state["summary_result"] = summary_result
        state["status"] = "ok"
        state["summary_errors"] = []
        state["retry_count"] = 0
    except Exception as e:
        state["status"] = "failed"
        # state["previous_code"] =
        state.setdefault("summary_errors", []).append(str(e))
        state["retry_count"] = state.get("retry_count", 0) + 1
    return state
