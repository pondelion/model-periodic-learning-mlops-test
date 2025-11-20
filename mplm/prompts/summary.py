"""
LLM prompt template for summary code generation.
"""

from langchain_core.prompts import PromptTemplate

SUMMARY_CODE_PROMPT= PromptTemplate.from_template(
    """
You are an expert data scientist. Based on the dataset metadata below,
generate Python code that computes a human-readable summary of the dataset.

The generated summary will later be used as part of the dataset understanding
and AI model design process, so ensure the summary provides meaningful,
accurate, and structured insights.

Examples:
- column names
- column data types
- number of rows
- missing value counts
- basic statistics if numeric
- useful info for categorical conversion decision

Code requirements:
- DO NOT load external data. Use the variables: df
- Return the summary as a Python string in a variable named summary_text

Dataset metadata (JSON-like):
{metadata}

Previous summary code execution error:
{summary_code_error}

Previous AI model training code execution error:
{training_code_error}

Output:
Only Python code, and always wrap it inside a markdown python block like this:
```python
# your code here
```
Do NOT provide any explanation outside the code block.
"""
)
