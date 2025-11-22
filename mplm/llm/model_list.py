import requests

from ..settings import settings

OPEN_ROUTER_FREE_MODEL_LIST = [
    # "deepseek/deepseek-chat-v3.1:free",
    "deepseek/deepseek-chat-v3-0324:free",  # NG
    "qwen/qwen3-coder:free",  # NG (rate limit error)
    "qwen/qwen3-14b:free",  # OK (but slow)
    "google/gemma-3-27b-it:free",  # NG (summary code execution fail)
    "google/gemini-2.0-flash-exp:free",  # NG (rate limit error)
    "openai/gpt-oss-20b:free",  # OK
    "mistralai/mistral-small-3.2-24b-instruct:free",  # OK (sometimes rate limit error)
    "meta-llama/llama-3.3-70b-instruct:free",  # OK
]
LOCAL_LLM_OLLAMA_LIST = [
    'gpt-oss:20b',
]


def get_openrouter_free_models() -> list[str]:
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    models = response.json().get("data", [])

    free_models = [m["id"] for m in models if m["id"].endswith(":free")]

    return free_models
