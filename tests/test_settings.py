from mplm.settings import settings


def assert_env_var_loaded(value, name):
    assert value is not None and value != "", f"設定 {name} が読み込まれていません。'.env' に値が設定されているか確認してください。"

def test_settings_loaded_from_env():
    """
    .env に記入された値が Settings に正しくロードされることを確認
    """
    # LLM
    assert_env_var_loaded(settings.openrouter_api_key, "OPENROUTER_API_KEY")
    assert_env_var_loaded(settings.llm_name, "LLM_NAME")

    # DB / モデル
    assert_env_var_loaded(settings.db_file, "DB_FILE")
    assert_env_var_loaded(settings.model_save_dir, "MODEL_SAVE_DIR")
    assert isinstance(settings.max_retry, int)
    assert isinstance(settings.default_random_seed, int)

    # GCP / Cloud Run / Artifact
    assert_env_var_loaded(settings.project_id, "PROJECT_ID")
    assert_env_var_loaded(settings.region, "REGION")
    assert_env_var_loaded(settings.artifact_repo_name, "ARTIFACT_REPO_NAME")
    assert_env_var_loaded(settings.bucket_name, "BUCKET_NAME")
    assert_env_var_loaded(settings.image_name, "IMAGE_NAME")
    assert_env_var_loaded(settings.github_repo, "GITHUB_REPO")
