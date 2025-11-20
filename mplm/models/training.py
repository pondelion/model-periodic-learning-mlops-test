"""
Models for training code generation and execution.
"""
from typing import Any

from pydantic import BaseModel, Field


class TrainCodeRequest(BaseModel):
    """
    Request for LLM to generate training and evaluation code.

    Attributes:
        summary_text: Summary of dataset produced earlier.
        train_split_seed: Seed for reproducible splitting.
    """
    summary_text: str = Field(description="Text summary of dataset.")
    train_split_seed: int = Field(description="Seed used for train/val/test splitting.")


class TrainExecutionResult(BaseModel):
    """
    Result of executing the training code.

    Attributes:
        accuracy: Accuracy on validation and test.
        model_path: Path to saved pickle model.
        code: The generated training code used for exec().
    """
    accuracy_val: float = Field(description="Validation accuracy.")
    accuracy_test: float = Field(description="Test accuracy.")
    code: str = Field(description="Generated training code used for execution.")
    model: Any = Field(description="Model instance trained via generated code")
    model_name: str = Field(description="Name of model trained via generated code")
    model_path: str | None = Field(default=None, description="Path to model pickle file.")
    llm_name: str | None = Field(default=None, description="LLM model name.")
