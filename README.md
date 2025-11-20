# model-periodic-learning-mlops-test

## Realtime Accuracy Summary

[Dashbord](https://pondelion.github.io/model-periodic-learning-mlops-test/)

![accuracy summary](https://storage.googleapis.com/model-periodic-learn-test/db/model_eval_results.png "Accuracy Summary")

[Download All Run Records CSV](https://storage.googleapis.com/model-periodic-learn-test/db/model_eval_results.csv)

## Deploy by Terraform

```bash
# .env のコメント行・空行を除外して、小文字に変換しつつ TF_VAR_ を付与して export
$ export $(grep -v -E '^\s*#|^\s*$' .env | \
  sed -E 's/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/TF_VAR_\L\1=\2/' | \
  xargs -d '\n')

# Terraform 用 SA の認証情報をセット
$ export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform_executor_sa_credentials.json"

# （初回のみ）アプリとGithub Action用SAとArtifact Registry だけ作成
$ terraform -chdir=deploy/terraform/pre init
$ terraform -chdir=deploy/terraform/pre plan
$ terraform -chdir=deploy/terraform/pre apply

# Docker イメージを build & push
$ docker build \
  -t ${TF_VAR_region}-docker.pkg.dev/${TF_VAR_project_id}/${TF_VAR_artifact_repo_name}/${TF_VAR_image_name}:latest \
  -f docker/Dockerfile .
$ docker push ${TF_VAR_region}-docker.pkg.dev/${TF_VAR_project_id}/${TF_VAR_artifact_repo_name}/${TF_VAR_image_name}:latest

# ↑preデプロイで取得したrun_exec_sa_email / github_trigger_sa_email / artifact_registry_repoを↓に環境変数経由で渡すためのsh実行
$ bash tf_pre_phase_outputs_to_env.sh
$ terraform -chdir=deploy/terraform/app init
# (アプリ修正後毎回) Cloud Runデプロイ
$ terraform -chdir=deploy/terraform/app plan
$ terraform -chdir=deploy/terraform/app apply
```

- GCS の CORS
```sh
$ echo '[{"origin":["*"],"method":["GET","HEAD"],"responseHeader":["Content-Type", "Access-Control-Allow-Origin"],"maxAgeSeconds":3600}]' > cors.json
$ gcloud storage buckets update gs://$BUCKET_NAME --cors-file=cors.json
$ rm cors.json
$ gsutil cors get gs://$BUCKET_NAME
```

## Local Run

```sh
# アプリ実行用 SA の認証情報をセット
$ export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/app_sa_credentials.json"

$ uv run python mplm/main.py
```