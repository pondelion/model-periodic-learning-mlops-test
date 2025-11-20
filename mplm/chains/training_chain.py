"""
LangGraph node: generate training code and execute it.
"""

from ..models.state import WorkflowState
from ..services.training_code_generator import generate_error_fixed_training_code, generate_training_code
from ..services.training_executor import execute_training_code
from ..utils.logger import get_logger

logger = get_logger(__name__)


def training_chain(state: WorkflowState) -> WorkflowState:
    """
    LangGraph node for generating and executing training code using LLM.

    This node generates Python training code via generate_training_code,
    executes it on the dataset, and updates the WorkflowState with the
    trained model, evaluation results, and any errors.

    Requires the state to have:
        - 'df': the dataset
        - 'summary_result': result from summary_chain
        - 'target_column': name of the target column
        - optional 'llm': LLM client instance

    Behavior:
        - On success:
            - state["training_result"] is updated with the execution result
            - state["status"] is set to "ok"
            - state["previous_errors"] is cleared
        - On failure:
            - state["status"] is set to "failed"
            - the generated code is stored in state["previous_code"]
            - the exception message is appended to state["previous_errors"]
            - state["retry_count"] is incremented
    """
    df = state["df"]
    summary = state["summary_result"]
    target_column = state["target_column"]

    logger.info("Generating training code with LLM...")
    try:
        code = None
        code = generate_training_code(summary, target_column, llm=state.get("llm", None))
        result = execute_training_code(
            df=df,
            code=code,
            model_output_path=state.get("model_output_path", None),
        )
        state["training_result"] = result
        state["status"] = "ok"
        # state["previous_errors"] = []
    except Exception as e:
        state["status"] = "failed"
        state["previous_code"] = code
        state.setdefault("training_errors", []).append(str(e))
        state["retry_count"] = state.get("retry_count", 0) + 1
    return state


def fix_error_training_chain(state: WorkflowState) -> WorkflowState:
    """
    LangGraph node for generating error-fixed training code + execution.

    Requires the state to have:
        - 'df': the dataset
        - 'target_column': target column name
        - 'previous_code': previously failed training code
        - 'previous_error': error message from last execution
    """
    df = state["df"]
    target_column = state["target_column"]
    previous_code = state["previous_code"]
    previous_errors = state["training_errors"]
    assert isinstance(previous_errors, list)
    assert len(previous_errors) > 0
    previous_error_str = '\n'.join(previous_errors)

    logger.info("Generating error-fixed training code with LLM...")

    try:
        fixed_code = previous_code
        fixed_code = generate_error_fixed_training_code(
            previous_code=previous_code,
            previous_error=previous_error_str,
            target_column=target_column,
            llm=state.get("llm", None),
        )
        result = execute_training_code(
            df=df,
            code=fixed_code,
            model_output_path=state.get("model_output_path", None),
        )
        state["training_result"] = result
        state["status"] = "ok"
        # state["training_errors"] = []
        state["fixed_code"] = fixed_code
    except Exception as e:
        state["status"] = "failed"
        state["previous_code"] = fixed_code
        state.setdefault("training_errors", []).append(str(e))
        state["retry_count"] = state.get("retry_count", 0) + 1

    return state
