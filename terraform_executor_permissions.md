# Terraform Executor SA — Required IAM Roles

Terraform で以下のリソースを作成します：
- Cloud Run
- GCS バケット
- Artifact Registry
- Service Account
- IAM bindings
- Workload Identity Federation（必要なら）

そのため Terraform Executor SA は以下のロールが必要です。

---

## 必須ロール（最小権限セット）

### Cloud Run 管理
- roles/run.admin

### GCS バケット作成・管理
- roles/storage.admin

### Artifact Registry 作成
- roles/artifactregistry.admin

### Service Account 作成
- roles/iam.serviceAccountAdmin

### Service Account Key（必要なら）
- roles/iam.serviceAccountKeyAdmin

### IAM Binding（ロール付与）
- roles/iam.securityAdmin

### Cloud Logging（Cloud Run が動くため）
- roles/logging.admin

---

```sh
# .env のコメント行・空行を除外して読み込む
$ export $(grep -v -E '^\s*#|^\s*$' .env | xargs)
```

- ルートアカウントログイン
```sh
$ gcloud auth login
```

## コマンド

```sh
$ export GCP_SA_EMAIL=$(gcloud iam service-accounts list \
  --project "$PROJECT_ID" \
  --filter="displayName:terraform-deploy" \
  --format="value(email)")
$ echo $GCP_SA_EMAIL
```

```sh
for role in \
  roles/run.admin \
  roles/storage.admin \
  roles/artifactregistry.admin \
  roles/iam.serviceAccountAdmin \
  roles/iam.serviceAccountKeyAdmin \
  roles/iam.securityAdmin \
  roles/logging.admin \
  roles/iam.workloadIdentityPoolAdmin \
  roles/iam.serviceAccountUser
do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$GCP_SA_EMAIL" \
    --role="$role"
done
```

## 必要な API を有効化

```sh
# gcloud に PROJECT_ID を設定
$ gcloud config set project $PROJECT_ID

# Artifact Registry API
$ gcloud services enable artifactregistry.googleapis.com
# IAM API
$ gcloud services enable iam.googleapis.com
# Clound Run API
$ gcloud services enable run.googleapis.com
```