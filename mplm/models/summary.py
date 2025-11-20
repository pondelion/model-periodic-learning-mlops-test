"""
Models for summary generation logic.
"""

from pydantic import BaseModel, Field


class SummaryGenerationRequest(BaseModel):
    """
    Request model passed to LLM for generating summary code.

    Attributes:
        dataset_metadata: JSON style metadata of dataset.
        require_code: Whether summary logic should be code.
    """

    dataset_metadata: dict = Field(
        description="Dictionary representation of dataset metadata."
    )
    require_code: bool = Field(
        description="If True: generate Python summary code; If False: use fixed summary logic."
    )


class SummaryResult(BaseModel):
    """
    Holds result of summary logic execution.

    Attributes:
        summary_text: Human readable summary string.
        summary_code: The actual summary code executed (None if fixed logic used).
    """

    summary_text: str = Field(description="Generated summary text.")
    summary_code: str | None = Field(
        default=None, description="Generated summary Python code."
    )
