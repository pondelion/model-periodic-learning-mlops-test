import pytest

from mplm.agent.automatic_model_build_agent import build_workflow
from mplm.models.state import WorkflowState
from mplm.services.data_loader import load_titanic_dataset


def test_workflow_end_to_end(request):
    """
    LangGraph workflow を実際の Titanic データでエンドツーエンド実行
    """
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番 LLM テストは --run-prod-tests を指定したときのみ実行")

    # Titanic データ読み込み
    df, metadata = load_titanic_dataset()

    # 初期 WorkflowState
    init_state: WorkflowState = {
        "df": df,
        "metadata": "not available",
        "target_column": "survived",
        "retry_count": 0,
        "summary_errors": [],
        "training_errors": [],
        "status": "",
        "previous_code": None,
        "previous_errors": [],
        "fixed_code": None,
    }

    # Workflow 構築 & コンパイル
    compiled_graph = build_workflow()  # 既に compile() 内で CompiledStateGraph を返す想定

    # stream を使って順にノードを処理
    final_state = None
    for state in compiled_graph.stream(init_state):
        final_state = state  # 最新状態を保持
        print(f"Processed node, current status: {state.get('status')}")

    print(final_state.keys())
    final_node = list(final_state.keys())[0]
    print(final_state[final_node]['retry_count'])
    final_state = final_state[final_node]
    final_state.pop("df")
    final_state.pop("previous_code")
    final_state.pop("fixed_code")
    # 最終状態確認
    assert final_state["status"] == "ok"
    assert final_state["summary_result"] is not None
    assert final_state["training_result"] is not None
    print("Workflow reached END successfully. Final state:", final_state)
