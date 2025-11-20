"""
Data models for Titanic dataset and metadata.
Used both for LLM prompts and internal state.
"""

from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    """
    Metadata extracted from the Titanic dataset.

    Attributes:
        columns: List of column names.
        dtypes: Dict of column -> dtype string.
        num_rows: Number of rows.
        missing_counts: Dict of column -> number of missing values.
    """

    columns: list[str] = Field(description="List of all column names in the dataset.")
    dtypes: dict[str, str] = Field(
        description="Mapping of column name to dtype string representation."
    )
    num_rows: int = Field(description="Total number of rows in the dataset.")
    missing_counts: dict[str, int] = Field(
        description="Mapping of column name to count of missing values."
    )
