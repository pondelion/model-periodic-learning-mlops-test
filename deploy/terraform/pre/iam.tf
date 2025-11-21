resource "google_service_account" "run_exec_sa" {
  account_id   = "cloudrun-ml-agent"
  display_name = "SA for ML Cloud Run execution"
}

resource "google_service_account" "github_trigger_sa" {
  account_id   = "github-trigger-invoker"
  display_name = "GitHub Actions SA to trigger Cloud Run"
}

resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-oidc-pool"
  display_name              = "GitHub Actions OIDC Pool"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub OIDC Provider"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }

  # ここで Provider の claim に合わせて条件を書く
  attribute_condition = "attribute.repository == '${var.github_repo}'"
}

resource "google_service_account_iam_member" "github_wif_binding" {
  service_account_id = google_service_account.github_trigger_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repo}"
}