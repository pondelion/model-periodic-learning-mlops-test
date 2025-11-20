import re


def extract_code_from_block(llm_output: str, lang: str = "python") -> str:
    """
    LLMの出力から指定した言語のコードブロックだけを抽出

    Args:
        llm_output: LLMが返した文字列
        lang: 抽出したいコードブロックの言語（例: "python", "bash"など）

    Returns:
        コードブロック内の文字列

    Raises:
        ValueError: 指定した言語のコードブロックが見つからない場合
    """
    pattern = rf"```{re.escape(lang)}(.*?)```"
    match = re.search(pattern, llm_output, re.DOTALL)
    if not match:
        raise ValueError(f"{lang} code block not found in LLM output")
    return match.group(1).strip()
