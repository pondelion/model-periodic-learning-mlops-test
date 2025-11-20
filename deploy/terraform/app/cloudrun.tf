resource "google_cloud_run_v2_service" "ml_agent" {
  name     = var.image_name
  location = var.region

  template {
    service_account = var.run_exec_sa_email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/${var.image_name}:latest"
      ports {
        container_port = 8080
      }

      env {
        name  = "MODEL_BUCKET"
        value = var.bucket_name
      }

      env {
        name  = "OPENROUTER_API_KEY"
        value = var.openrouter_api_key
      }

      env {
        name  = "LLM_NAME"
        value = var.llm_name
      }

      env {
        name  = "DB_FILE"
        value = var.db_file
      }

      env {
        name  = "DEFAULT_RANDOM_SEED"
        value = tostring(var.default_random_seed)
      }

      env {
        name  = "MAX_RETRY"
        value = tostring(var.max_retry)
      }

      env {
        name  = "MODEL_SAVE_DIR"
        value = var.model_save_dir
      }
    }
  }
}