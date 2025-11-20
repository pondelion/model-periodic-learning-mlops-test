from unittest.mock import patch

import pandas as pd
import pytest

from mplm.chains.summary_chain import summary_chain
from mplm.models.state import WorkflowState
from mplm.models.summary import SummaryResult


def make_state():
    return WorkflowState(
        df=pd.DataFrame({"a": [1, 2], "b": [3, 4]}),
        summary_errors=[],
        training_errors=[],
        retry_count=0,
        status="init",
    )


# ----------------------------------------------------------------------
# Mock 版テスト（成功系）
# ----------------------------------------------------------------------
def test_summary_chain_success():
    state = make_state()

    fake_summary = SummaryResult(
        summary_text="ok summary",
        summary_code="pass",
    )

    with patch(
        "mplm.chains.summary_chain.generate_summary_with_llm",
        return_value=fake_summary,
    ) as mock_summary:

        updated = summary_chain(state)

        mock_summary.assert_called_once()
        assert updated["status"] == "ok"
        assert updated["summary_result"] == fake_summary
        assert updated["summary_errors"] == []
        assert updated["retry_count"] == 0


# ----------------------------------------------------------------------
# Mock 版テスト（失敗系）
# ----------------------------------------------------------------------
def test_summary_chain_failure():
    state = make_state()

    with patch(
        "mplm.chains.summary_chain.generate_summary_with_llm",
        side_effect=Exception("summary boom"),
    ) as mock_summary:

        updated = summary_chain(state)

        mock_summary.assert_called_once()
        assert updated["status"] == "failed"
        assert "summary boom" in updated["summary_errors"][-1]
        assert updated["retry_count"] == 1


# ----------------------------------------------------------------------
# 本番 LLM テスト
# ----------------------------------------------------------------------
def test_summary_chain_prod(request):
    """
    実際の LLM を呼び出す summary_chain テスト。
    --run-prod-tests が指定されたときのみ実行
    """
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番 LLM テストは --run-prod-tests を指定したときのみ実行")

    # state を準備
    state = WorkflowState(
        df=pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]}),
        summary_errors=[],
        training_errors=[],
        retry_count=0,
        status="init",
    )

    updated = summary_chain(state)

    print("===== Generated summary result =====")
    print(updated.get("summary_result").summary_text)
    print("===================================")
    print(updated.get("summary_result").summary_code)
    print("===================================")

    # 結果の確認
    assert updated["status"] == "ok"
    assert isinstance(updated["summary_result"], SummaryResult)
    assert updated["summary_result"].summary_text is not None
    assert len(updated["summary_result"].summary_text) > 0
