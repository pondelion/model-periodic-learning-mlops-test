from unittest.mock import patch

import pytest

from mplm.chains.summary_chain import summary_chain
from mplm.chains.training_chain import training_chain
from mplm.llm.client import get_llm
from mplm.models.state import WorkflowState
from mplm.models.summary import SummaryResult
from mplm.models.training import TrainExecutionResult
from mplm.services.data_loader import load_titanic_dataset


# ============================================================
# 1. モック版（training_chain 単体テスト）
# ============================================================
def test_training_chain_mock():
    # ---- 事前 state ----
    df, metadata = load_titanic_dataset()

    state: WorkflowState = {
        "df": df,
        "summary_result": SummaryResult(
            summary_text="some summary",
            summary_code="pass"
        ),
        "summary_errors": [],
        "training_errors": [],
        "retry_count": 0,
        "target_column": "survived",
    }

    # ---- モック ----
    fake_training_result = TrainExecutionResult(
        llm_name=None,
        accuracy_val=0.91,
        accuracy_test=0.88,
        model_path=None,
        code="FAKE_TRAINING_CODE",
        model="FAKE",
        model_name="FAKE",
    )

    with patch(
        "mplm.chains.training_chain.generate_training_code",
        return_value="FAKE_TRAINING_CODE"
    ) as mock_gen:

        with patch(
            "mplm.chains.training_chain.execute_training_code",
            return_value=fake_training_result
        ) as mock_exec:

            updated = training_chain(state)

            # 呼び出し確認
            mock_gen.assert_called_once()
            mock_exec.assert_called_once()

            # 状態確認
            assert updated["status"] == "ok"
            assert updated["training_result"] == fake_training_result
            assert updated["training_errors"] == []
            assert updated["retry_count"] == 0


# ============================================================
# 2. モック（LLM 生成コードが失敗するケース）
# ============================================================
def test_training_chain_failure():
    df, metadata = load_titanic_dataset()

    state: WorkflowState = {
        "df": df,
        "summary_result": SummaryResult(
            summary_text="some summary",
            summary_code="pass"
        ),
        "summary_errors": [],
        "training_errors": [],
        "retry_count": 0,
        "target_column": "survived",
    }

    with patch(
        "mplm.chains.training_chain.generate_training_code",
        side_effect=RuntimeError("LLM failed")
    ):
        updated = training_chain(state)

        assert updated["status"] == "failed"
        assert "LLM failed" in updated["training_errors"][-1]
        assert updated["retry_count"] == 1


# ============================================================
# 3. 本番テスト（summary_chain → training_chain）
# ============================================================
def test_training_chain_prod(request):
    """
    実際の Titanic データを使い、
    summary_chain → training_chain の流れを通す。
    """
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番テストは --run-prod-tests 指定時のみ実行")

    df, metadata = load_titanic_dataset()

    # ---- 初期 state ----
    state: WorkflowState = {
        "df": df,
        "metadata": metadata,
        "summary_errors": [],
        "training_errors": [],
        "retry_count": 0,
        "target_column": "survived",
    }

    # ---- LLM ----
    llm = get_llm(temperature=1.4)
    state['llm'] = llm

    # ---- summary_chain ----
    state = summary_chain(state)

    print("\n====== Summary Result ======")
    print(state["summary_result"].summary_code)
    print(state["summary_result"].summary_text)
    print("============================\n")

    assert state["status"] == "ok"
    assert state["summary_result"] is not None

    # ---- training_chain ----
    state = training_chain(state)

    print("\n====== Training Result ======")
    tr = state["training_result"]
    print("accuracy_val:", tr.accuracy_val)
    print("accuracy_test:", tr.accuracy_test)
    print("model_name:", tr.model_name)
    print("model_path:", tr.model_path)
    print("code:", tr.code)
    print("============================\n")

    assert state["status"] == "ok"
    assert tr.accuracy_val is not None
    assert tr.accuracy_test is not None
