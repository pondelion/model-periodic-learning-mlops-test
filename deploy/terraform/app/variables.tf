variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region for Cloud Run"
  default     = "us-central1"
}

variable "bucket_name" {
  type        = string
  description = "GCS bucket to store model artifacts & sqlite"
}

variable "image_name" {
  type    = string
  default = "ml-titanic-agent"
}

variable "artifact_repo_name" {
  type    = string
  description = "Artifact Registry name from pre phase"
}

variable "run_exec_sa_email" {
  type        = string
  description = "Cloud Run execution service account email from pre phase"
}

variable "github_trigger_sa_email" {
  type        = string
  description = "GutHub action service account email from pre phase"
}

# OpenRouter / LLM 設定
variable "openrouter_api_key" {
  type        = string
  description = "API key for OpenRouter"
}

variable "llm_name" {
  type        = string
  description = "LLM model name"
}

# SQLite 設定
variable "db_file" {
  type        = string
  description = "SQLite database file path"
}

# その他設定
variable "default_random_seed" {
  type    = number
  default = 42
}

variable "max_retry" {
  type    = number
  default = 3
}

variable "model_save_dir" {
  type    = string
  default = "./models_saved"
}

variable "image_digest" {
  type = string
}