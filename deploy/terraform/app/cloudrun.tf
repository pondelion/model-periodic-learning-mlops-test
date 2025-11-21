resource "google_cloud_run_v2_job" "mplm_app_job" {
  name     = var.image_name
  location = var.region
  deletion_protection = false  # 削除保護を無効にする

  template {
    # template 内に containers 設定
    template {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/${var.image_name}:latest"

        resources {
          limits = {
            cpu    = "2"
            memory = "1024Mi"
          }
        }

        env {
          name  = "BUCKET_NAME"
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
      timeout = "1800s"
      service_account = var.run_exec_sa_email
      max_retries = 2
    }
  }
}

resource "google_cloud_run_v2_job_iam_member" "invoker_binding" {
  location = google_cloud_run_v2_job.mplm_app_job.location
  name     = google_cloud_run_v2_job.mplm_app_job.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.github_trigger_sa_email}"
}

resource "google_cloud_run_v2_job_iam_member" "viewer_binding" {
  location = google_cloud_run_v2_job.mplm_app_job.location
  name     = google_cloud_run_v2_job.mplm_app_job.name
  role     = "roles/run.viewer"
  member   = "serviceAccount:${var.github_trigger_sa_email}"
}
