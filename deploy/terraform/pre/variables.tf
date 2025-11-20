variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
  default     = "us-central1"
}

variable "artifact_repo_name" {
  type    = string
  default = "ml-models"
}

variable "github_repo" {
  type        = string
  description = "GitHub repo: e.g. user/repo"
}

variable "bucket_name" {
  type        = string
  description = "GCS bucket to store model artifacts & sqlite"
}
