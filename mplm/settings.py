"""
Application configuration using pydantic-settings.
Loads environment variables from .env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.

    Attributes:
        openrouter_api_key: API key for OpenRouter (required for LLM).
        llm_name: Optional model name. If None → must be set in .env.
        db_file: SQLite database file path.
        model_save_dir: Directory to store trained model binaries.
        max_retry: Maximum retry count for LLM-generated code execution.
        default_random_seed: Seed for train/val/test splitting.
        project_id: GCP Project ID.
        region: GCP region.
        artifact_repo_name: Artifact Registry repository name.
        bucket_name: GCS bucket name.
        image_name: Docker image name.
        github_repo: GitHub repository.
    """

    openrouter_api_key: str
    llm_name: str | None

    db_file: str = "./db/model_eval_results.db"
    model_save_dir: str = "./models_saved"
    max_retry: int = 3
    default_random_seed: int = 42

    project_id: str | None = None
    region: str = "asia-northeast1"
    artifact_repo_name: str | None = None
    bucket_name: str
    image_name: str | None = None
    github_repo: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def db_file_gcs(self) -> str:
        """
        Returns GCS path for storing the SQLite file inside the bucket.

        Example:
            gs://my-bucket/db/titanic_models.db
        """
        normalized = self.db_file.lstrip("./").lstrip("/")
        return f"gs://{self.bucket_name}/{normalized}"

    @property
    def result_csv_public_url(self) -> str:
        csv_filepath = self.db_file.lstrip("./").lstrip("/").replace('.db', '.csv')
        return f"https://storage.googleapis.com/{self.bucket_name}/{csv_filepath}"

    def print_settings(self) -> None:
        """
        Pretty-print all settings except sensitive fields like openrouter_api_key.
        """
        # exclude secret keys
        visible_dict = self.model_dump(exclude={"openrouter_api_key"})
        max_key_len = max(len(k) for k in visible_dict)
        print("\nApplication Settings:")
        for key, value in visible_dict.items():
            print(f"  {key.ljust(max_key_len)} : {value}")


settings = Settings()
