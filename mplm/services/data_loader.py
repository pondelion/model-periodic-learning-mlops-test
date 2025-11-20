"""
Load Titanic dataset using scikit-learn.
"""

import pandas as pd
from sklearn.datasets import fetch_openml

from ..models.data import DatasetMetadata


def load_titanic_dataset() -> tuple[pd.DataFrame, DatasetMetadata]:
    """
    Load Titanic dataset from scikit-learn (OpenML).

    Returns:
        df: pandas DataFrame
        metadata: DatasetMetadata extracted from df
    """

    dataset = fetch_openml("titanic", version=1, as_frame=True)
    df = dataset.frame

    metadata = DatasetMetadata(
        columns=list(df.columns),
        dtypes={col: str(df[col].dtype) for col in df.columns},
        num_rows=len(df),
        missing_counts=df.isna().sum().to_dict(),
    )

    return df, metadata
