"""
Automatic Model Build Agent using LangGraph.

This module defines the workflow and database integration for
automatic model building, including dataset summarization and
model training with retry logic. All nodes are wired together
using LangGraph's StateGraph.
"""

from langgraph.graph import END, StateGraph

from ..chains.summary_chain import summary_chain
from ..chains.training_chain import fix_error_training_chain, training_chain
from ..db.crud import create_run_record
from ..db.session import get_session
from ..llm import get_llm
from ..models.state import WorkflowState
from ..settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


def build_workflow(max_retry: int = settings.max_retry):
    """
    Build the automatic model build workflow as a LangGraph StateGraph.

    Workflow nodes:
      - summary: generate dataset summary using LLM
      - training: train model
      - fix_error_training: retry training if errors occur

    Retry logic:
      - summary failure → retry summary up to `max_retry`
      - training failure → retry fix_error_training up to `max_retry`
      - fix_error_training failure → retry itself up to `max_retry`
      - success → END
    """
    graph = StateGraph(WorkflowState)

    # Add nodes
    graph.add_node("summary", summary_chain)
    graph.add_node("training", training_chain)
    graph.add_node("fix_error_training", fix_error_training_chain)

    # Entry point
    graph.set_entry_point("summary")

    # Summary node retry → summary
    graph.add_conditional_edges(
        "summary",
        lambda state: "retry" if (state.get("status") == "failed" and state.get("retry_count", 0) < max_retry) else
                      "next" if state.get("status") == "ok" else
                      "end",
        {
            "retry": "summary",
            "next": "training",
            "end": END,
        },
    )

    # Training node retry → fix_error_training
    graph.add_conditional_edges(
        "training",
        lambda state: "retry" if (state.get("status") == "failed" and state.get("retry_count", 0) < max_retry) else
                      "next" if state.get("status") == "ok" else
                      "end",
        {
            "retry": "fix_error_training",
            "next": END,
            "end": END,
        },
    )

    # FixErrorTraining node retry → fix_error_training itself
    graph.add_conditional_edges(
        "fix_error_training",
        lambda state: "retry" if (state.get("status") == "failed" and state.get("retry_count", 0) < max_retry) else
                      "next" if state.get("status") == "ok" else
                      "end",
        {
            "retry": "fix_error_training",
            "next": END,
            "end": END,
        },
    )

    return graph.compile()


def save_run_to_db(state: WorkflowState, db_path: str = settings.db_file):
    """
    Save summary and training results into the database using the new RunRecord schema.
    db_path は指定がなければ settings.db_file を使用する。
    """
    training = state.get("training_result")
    summary = state.get("summary_result")

    if not training:
        logger.warning("No training_result found in state, skipping DB save.")
        return

    if not summary:
        logger.warning("No summary_result found in state, dataset_summary will be empty.")

    # Extract fields safely
    dataset_summary_code = getattr(summary, "summary_code", None) if summary else None
    dataset_summary = getattr(summary, "summary_text", "") if summary else ""
    train_code = getattr(training, "code", "")
    model_name = getattr(training, "model_name", "")
    model_path = getattr(training, "model_path", "")
    accuracy_val = getattr(training, "accuracy_val", 0.0)
    accuracy_test = getattr(training, "accuracy_test", 0.0)

    # LLM name resolution
    llm = state.get("llm", None) or get_llm()
    if hasattr(llm, "model"):
        llm_name = llm.model
    elif hasattr(llm, "model_name"):
        llm_name = llm.model_name
    else:
        llm_name = "unknown"

    # Create session dynamically
    SessionLocal = get_session(db_path)
    with SessionLocal() as db:
        create_run_record(
            db,
            train_code=train_code,
            model_name=model_name,
            model_path=model_path,
            dataset_summary=dataset_summary,
            dataset_summary_code=dataset_summary_code,
            accuracy_val=accuracy_val,
            accuracy_test=accuracy_test,
            llm_name=llm_name,
        )

    logger.info("Saved run to DB.")
