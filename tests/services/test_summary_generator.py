from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from mplm.models.data import DatasetMetadata
from mplm.models.summary import SummaryResult
from mplm.services.data_loader import load_titanic_dataset
from mplm.services.summary_generator import fixed_summary_logic, generate_summary_with_llm
from mplm.utils.exceptions import CodeExecutionError


# fixed_summary_logicのテスト
def test_fixed_summary_logic():
    """fixed_summary_logic関数のテスト"""
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
    }
    df = pd.DataFrame(data)

    result = fixed_summary_logic(df)

    assert "Rows: 3" in result
    assert "Name: object" in result
    assert "Age: int64" in result
    assert "missing=0" in result


# generate_summary_with_llmのテスト（モックを使用）
@patch("mplm.services.summary_generator.get_llm")
def test_generate_summary_with_llm(mock_get_llm):
    """generate_summary_with_llm関数のテスト"""
    # モック設定
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = """
```python
summary_text = 'This is a summary'
```
""".strip()

    # モックデータ
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
    }
    df = pd.DataFrame(data)
    metadata = DatasetMetadata(
        columns=["Name", "Age"],
        dtypes={"Name": "object", "Age": "int64"},
        num_rows=3,
        missing_counts={"Name": 0, "Age": 0},
    )

    result = generate_summary_with_llm(df, metadata)

    assert isinstance(result, SummaryResult)
    assert result.summary_text == "This is a summary"


# generate_summary_with_llmのエラーハンドリングテスト
@patch("mplm.services.summary_generator.get_llm")
def test_generate_summary_with_llm_error(mock_get_llm):
    """generate_summary_with_llm関数のエラーハンドリングテスト"""
    # モック設定
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = """
```python
summary_text = None
```
""".strip()  # summary_textがNone

    # モックデータ
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
    }
    df = pd.DataFrame(data)
    metadata = DatasetMetadata(
        columns=["Name", "Age"],
        dtypes={"Name": "object", "Age": "int64"},
        num_rows=3,
        missing_counts={"Name": 0, "Age": 0},
    )

    with pytest.raises(CodeExecutionError, match="summary_text variable not produced by LLM code"):
        generate_summary_with_llm(df, metadata)


# 本番テスト
def test_generate_summary_with_llm_prod(request):
    """本番のgenerate_summary_with_llm関数のテスト"""
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番のテストは --run-prod-tests を指定しないとスキップされます")

    # 本番のデータセット
    df, metadata = load_titanic_dataset()

    # テスト実行
    result = generate_summary_with_llm(df, 'not available', debug=True)
    print("====================== generated summary code ==============================")
    print(result.summary_code)
    print("====================== generated summary text ==============================")
    print(result.summary_text)
    print("============================================================================")

    # 結果の確認
    assert isinstance(result, SummaryResult)
    assert result.summary_text is not None  # summary_textが適切に生成されているか

