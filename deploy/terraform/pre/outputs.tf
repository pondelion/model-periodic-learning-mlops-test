output "run_exec_sa_email" {
  value = google_service_account.run_exec_sa.email
}

output "github_trigger_sa_email" {
  value = google_service_account.github_trigger_sa.email
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.docker_repo.repository_id
}