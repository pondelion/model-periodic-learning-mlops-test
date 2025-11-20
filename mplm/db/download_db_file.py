"""
Utility for downloading SQLite DB file from GCS to local storage.

Used explicitly before initializing SQLAlchemy engine to avoid
unexpected overwriting caused by global module import timing.
"""

from pathlib import Path

from mplm.settings import settings
from mplm.utils.gcs import download_file_from_gcs, gcs_exists
from mplm.utils.logger import get_logger

logger = get_logger(__name__)


def download_db_from_gcs_if_exists(
    *,
    local_db_path: str | Path | None = None,
    gcs_db_path: str | None = None,
    overwrite: bool = True,
) -> Path | None:
    """
    Download SQLite DB from GCS → local path if GCS object exists.

    Parameters
    ----------
    local_db_path : str | Path | None
        Local path where SQLite DB should be saved.
        Defaults to settings.db_file.
    gcs_db_path : str | None
        GCS path (gs://bucket/path/to/dbfile).
        Defaults to settings.db_file_gcs.
    overwrite : bool
        If True, always overwrite local file.
        If False, download only if local file does not exist.

    Returns
    -------
    Path | None
        Returns local DB path if downloaded or already present.
        Returns None if GCS file does not exist or download fails.
    """

    # Default arguments from settings
    local_db_path = Path(local_db_path or settings.db_file)
    gcs_db_path = gcs_db_path or settings.db_file_gcs

    # Ensure directory exists
    local_db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Checking GCS for DB file: {gcs_db_path}")

        if not gcs_exists(gcs_db_path):
            logger.info("GCS DB file does not exist. Skipping download.")
            return None

        if local_db_path.exists() and not overwrite:
            logger.info(f"Local DB exists (overwrite=False). Skip download: {local_db_path}")
            return local_db_path

        logger.info(f"Downloading DB from GCS → {local_db_path}")
        download_file_from_gcs(gcs_db_path, local_db_path)
        logger.info("Download completed.")
        return local_db_path

    except Exception as e:
        logger.warning(f"Failed checking/downloading DB from GCS: {e}")
        raise e
