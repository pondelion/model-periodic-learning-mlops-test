from unittest.mock import MagicMock, patch

import pytest
from langchain_classic.schema import HumanMessage

from mplm import settings
from mplm.llm.client import get_llm
from mplm.utils.exceptions import LLMConfigError


@pytest.fixture
def mock_settings(monkeypatch):
    """
    settings.settings インスタンスの値を単体テスト用にリセット
    """
    monkeypatch.setattr(settings.settings, "llm_name", "default-model")
    monkeypatch.setattr(settings.settings, "openrouter_api_key", "fake-api-key")


def test_get_llm_with_explicit_model(mock_settings):
    mock_chat = MagicMock()
    with patch("mplm.llm.client.ChatOpenAI", return_value=mock_chat) as mock_class:
        llm = get_llm("explicit-model")
        mock_class.assert_called_once_with(
            model="explicit-model",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key="fake-api-key",
            temperature=None,
        )
        assert llm is mock_chat


def test_get_llm_with_default_model(mock_settings):
    mock_chat = MagicMock()
    with patch("mplm.llm.client.ChatOpenAI", return_value=mock_chat) as mock_class:
        llm = get_llm(None)
        mock_class.assert_called_once_with(
            model="default-model",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key="fake-api-key",
            temperature=None,
        )
        assert llm is mock_chat


def test_get_llm_raises_if_no_model(mock_settings, monkeypatch):
    monkeypatch.setattr(settings.settings, "llm_name", None)
    with pytest.raises(LLMConfigError) as excinfo:
        get_llm(None)
    assert "OpenRouter model name is not set" in str(excinfo.value)


@pytest.mark.skipif(
    not hasattr(settings.settings, "openrouter_api_key") or
    not settings.settings.openrouter_api_key,
    reason="OPENROUTER_API_KEY が設定されていないため"
)
def test_live_llm_call(request):
    """
    実際の OpenRouter LLM に問い合わせる統合テスト。
    settings.settings にセットされた API_KEY と MODEL_NAME を使用。
    """
    if not request.config.getoption("--run-prod-tests"):
        pytest.skip("本番のテストは --run-prod-tests を指定しないとスキップされます")
    llm = get_llm()  # 本物の設定で呼び出す

    messages = [HumanMessage(content="Hello, how are you?")]

    response = llm.invoke(messages)

    text = response.content

    print("LLM Response:", text)

    assert text is not None
