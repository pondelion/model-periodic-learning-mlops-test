from pathlib import Path

from google.cloud import storage


def get_gcs_client() -> storage.Client:
    """
    Returns a GCS client using application default credentials.
    GOOGLE_APPLICATION_CREDENTIALS must be set unless running on GCP.
    """
    return storage.Client()


def parse_gcs_path(gcs_path: str) -> tuple[str, str]:
    """
    Parse a GCS path like 'gs://bucket/path/to/file'
    → returns (bucket_name, blob_path)
    """
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_path}")

    without_scheme = gcs_path[5:]
    parts = without_scheme.split("/", 1)
    bucket = parts[0]
    blob_path = parts[1] if len(parts) > 1 else ""

    return bucket, blob_path


# -------------------------------------------------------
# 1. Upload
# -------------------------------------------------------
def upload_file_to_gcs(
    local_path: str | Path,
    gcs_path: str,
    *,
    make_public: bool = False,
) -> str:
    """
    Upload a local file to GCS.

    Args:
        local_path: Local file path
        gcs_path: 'gs://bucket/path/to/file'
        make_public: Whether to make the uploaded file publicly readable (default: False)

    Returns:
        If make_public=True → the public HTTPS URL
        If make_public=False → the original gcs_path (gs://...)
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local file not found: {local_path}")

    bucket_name, blob_path = parse_gcs_path(gcs_path)
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    # Upload file
    blob.upload_from_filename(str(local_path))

    # Optionally make public
    if make_public:
        blob.make_public()
        return blob.public_url  # → https://storage.googleapis.com/bucket/file

    return gcs_path  # Keep gs:// path for private files


# -------------------------------------------------------
# 2. Download
# -------------------------------------------------------
def download_file_from_gcs(gcs_path: str, local_path: str | Path) -> Path:
    """
    Download a GCS file to local.

    Args:
        gcs_path: GCS path
        local_path: desired local save path

    Returns:
        Path to downloaded local file
    """
    bucket_name, blob_path = parse_gcs_path(gcs_path)
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    blob.download_to_filename(str(local_path))
    return local_path


# -------------------------------------------------------
# 3. Exists?
# -------------------------------------------------------
def gcs_exists(gcs_path: str) -> bool:
    """
    Check if a GCS file exists.

    Args:
        gcs_path: 'gs://bucket/path/to/file'
    Returns:
        True if exists, False otherwise
    """
    bucket_name, blob_path = parse_gcs_path(gcs_path)
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    return blob.exists()
