from unittest.mock import MagicMock, patch

import pytest

from mplm.services.training_code_generator import generate_training_code


@patch("mplm.services.training_code_generator.get_llm")
@patch("mplm.services.training_code_generator.extract_code_from_block")
def test_generate_training_code(mock_extract_code, mock_get_llm):
    """generate_training_code関数の正常系テスト"""

    # モック LLM
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = "python\nprint(\"Training code\")\n"

    # extract_code_from_block の戻り値
    mock_extract_code.return_value = 'print("Training code")'

    summary = "Rows: 100\nColumns: age, fare"
    target_column = "survived"

    code = generate_training_code(summary, target_column, seed=123)

    # 返却コードの確認
    assert code == 'print("Training code")'

    # LLM呼び出しが適切に行われたか
    mock_llm.invoke.assert_called_once()
    assert "Rows: 100" in mock_llm.invoke.call_args[0][0]
    assert "survived" in mock_llm.invoke.call_args[0][0]

    # extract_code_from_block が LLM出力を処理したか
    mock_extract_code.assert_called_once()


@patch("mplm.services.training_code_generator.get_llm")
@patch("mplm.services.training_code_generator.extract_code_from_block")
def test_generate_training_code_empty(mock_extract_code, mock_get_llm):
    """extract_code_from_block が空文字を返したときのテスト"""

    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = "python\n# no code\n"

    mock_extract_code.return_value = "" # コード抽出失敗

    summary = "dummy"
    target_column = "y"

    code = generate_training_code(summary, target_column)

    # 空文字がそのまま返る仕様
    assert code == ""


def test_generate_training_code_prod(request):
    """本番の generate_training_code の LLM 呼び出しテスト"""
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番 LLM テストは --run-prod-tests を指定した時のみ実行")

    summary = "Rows: 3\nColumns: Name, Age"
    target_column = "Survived"

    code = generate_training_code(summary, target_column)

    print("====================== generated training code ==============================")
    print(code)
    print("============================================================================")

    assert isinstance(code, str)
    assert len(code) > 0
