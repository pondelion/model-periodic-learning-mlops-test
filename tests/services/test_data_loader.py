from mplm.models.data import DatasetMetadata
from mplm.services.data_loader import load_titanic_dataset


def test_load_titanic_dataset():
    """Titanicデータセットの読み込みテスト"""
    df, metadata = load_titanic_dataset()

    assert df is not None
    assert not df.empty
    assert isinstance(metadata, DatasetMetadata)
    assert "pclass" in df.columns
    assert "age" in df.columns
    assert isinstance(metadata.num_rows, int)
    assert isinstance(metadata.missing_counts, dict)
