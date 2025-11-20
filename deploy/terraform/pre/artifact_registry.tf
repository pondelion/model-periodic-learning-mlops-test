resource "google_artifact_registry_repository" "docker_repo" {
  provider      = google
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "Docker repo for ML agent"
  format        = "DOCKER"
}
