from unittest.mock import MagicMock, patch

from mplm.agent.automatic_model_build_agent import save_run_to_db
from mplm.models.state import WorkflowState
from mplm.models.summary import SummaryResult
from mplm.models.training import TrainExecutionResult


def test_save_run_to_db_success():
    # モックオブジェクトの作成
    mock_training_result = TrainExecutionResult(
        accuracy_val=0.9,
        accuracy_test=0.85,
        code="train_code_here",
        model="mock_model",
        model_name="mock_model_name",
        model_path="/tmp/mock_model.pkl",
        llm_name="mock_llm",
    )
    mock_summary_result = SummaryResult(
        summary_text="This is a summary",
        summary_code="summary_code_here",
    )
    mock_llm = MagicMock()
    mock_llm.model = "mock_llm"

    state: WorkflowState = {
        "df": None,
        "metadata": None,
        "target_column": "target",
        "summary_result": mock_summary_result,
        "training_result": mock_training_result,
        "retry_count": 0,
        "summary_errors": [],
        "training_errors": [],
        "status": "ok",
        "previous_code": None,
        "previous_errors": [],
        "fixed_code": None,
        "use_fixed_summary": False,
        "llm": mock_llm,
    }

    with patch("mplm.agent.automatic_model_build_agent.create_run_record") as mock_create, \
         patch("mplm.agent.automatic_model_build_agent.get_session") as mock_get_session:

        # get_session() が返す SessionLocal をモック
        mock_sessionmaker = MagicMock()
        mock_db = MagicMock()

        # SessionLocal().__enter__() → db
        mock_sessionmaker.return_value.__enter__.return_value = mock_db

        # get_session が sessionmaker を返すモックに差し替えられる
        mock_get_session.return_value = mock_sessionmaker

        save_run_to_db(state)

        # create_run_record が正しく呼ばれたことを確認
        mock_create.assert_called_once_with(
            mock_db,
            train_code="train_code_here",
            model_name="mock_model_name",
            model_path="/tmp/mock_model.pkl",
            dataset_summary="This is a summary",
            dataset_summary_code="summary_code_here",
            accuracy_val=0.9,
            accuracy_test=0.85,
            llm_name="mock_llm",
        )
