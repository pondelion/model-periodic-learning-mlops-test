"""
ORM table definitions.
"""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class RunRecord(Base):
    """
    Stores metadata about each training run.

    Columns:
        id: Primary key.
        dataset_summary_code: Code used for dataset summarization.
        train_code: Code used for training model.
        model_path: File path of saved model.
        accuracy_val: Validation accuracy.
        accuracy_test: Test accuracy.
        created_at: Timestamp when record was created.
    """

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    llm_name = Column(String(255), nullable=True)

    dataset_summary_code = Column(Text, nullable=True)
    dataset_summary = Column(Text, nullable=False)
    train_code = Column(Text, nullable=False)

    model_name = Column(Text, nullable=False)
    model_path = Column(String(255), nullable=True)

    accuracy_val = Column(Float, nullable=False)
    accuracy_test = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
