"""
LangChain LLM client for OpenRouter models.
"""

from langchain_openai import ChatOpenAI

from ..settings import settings
from ..utils.exceptions import LLMConfigError
from .model_list import LOCAL_LLM_OLLAMA_LIST


def get_llm(
    model_name: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """
    Create a LangChain ChatOpenAI object connected to OpenRouter.

    Args:
        model_name: Optional override. If None → use settings.llm_name.

    Returns:
        ChatOpenAI: Ready-to-use OpenRouter LLM client.
    """

    resolved_model = model_name or settings.llm_name

    if resolved_model is None:
        raise LLMConfigError(
            "OpenRouter model name is not set. "
            "Please set LLM_NAME in your .env."
        )

    if resolved_model in LOCAL_LLM_OLLAMA_LIST:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model=resolved_model, temperature=temperature)
    else:
        return ChatOpenAI(
            model=resolved_model,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=settings.openrouter_api_key,
            temperature=temperature,
        )
