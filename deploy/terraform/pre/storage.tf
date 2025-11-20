resource "google_storage_bucket" "model_bucket" {
  name     = var.bucket_name
  location = var.region
  versioning {
    enabled = true
  }

  cors {
    origin          = ["*"]                # アクセス許可したいオリジン
    method          = ["GET", "HEAD"]      # 許可するHTTPメソッド
    response_header = ["Content-Type"]      # 許可するレスポンスヘッダ
    max_age_seconds = 3600                  # キャッシュ時間
  }
}

resource "google_storage_bucket_iam_member" "run_sa_bucket_write" {
  bucket = google_storage_bucket.model_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.run_exec_sa.email}"
}
