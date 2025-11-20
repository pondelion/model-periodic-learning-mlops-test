"""
CRUD helper functions for database operations.
"""

import pandas as pd
from sqlalchemy.orm import Session

from .models import RunRecord
from .session import get_session


def create_run_record(
    db: Session,
    *,
    train_code: str,
    model_name: str,
    model_path: str,
    dataset_summary: str,
    accuracy_val: float,
    accuracy_test: float,
    dataset_summary_code: str | None = None,
    llm_name: str | None = None,
) -> RunRecord:
    """
    Insert new RunRecord into the database.
    """
    if db is None:
        LocalSession = get_session()
        db = LocalSession()

    record = RunRecord(
        dataset_summary=dataset_summary,
        dataset_summary_code=dataset_summary_code,
        train_code=train_code,
        model_name=model_name,
        model_path=model_path,
        accuracy_val=accuracy_val,
        accuracy_test=accuracy_test,
        llm_name=llm_name,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_records_as_df(db: Session | None = None) -> pd.DataFrame:
    """
    Fetch all RunRecord entries from the database and return as a pandas DataFrame.
    """
    if db is None:
        LocalSession = get_session()
        db = LocalSession()

    records = db.query(RunRecord).all()

    # SQLAlchemyオブジェクトを辞書に変換
    records_dicts = [r.__dict__.copy() for r in records]
    for d in records_dicts:
        d.pop("_sa_instance_state", None)  # 内部用属性を削除

    df = pd.DataFrame(records_dicts)
    return df
