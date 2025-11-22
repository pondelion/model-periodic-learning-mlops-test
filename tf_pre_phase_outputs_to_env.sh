#!/bin/bash
# pre_phase_outputs_to_env.sh
# deploy/terraform/pre の出力を環境変数に変換して export

# Terraform の出力を JSON で取得
outputs_json=$(terraform -chdir=deploy/terraform/pre output -json)

# jq が必要
# JSON 内の各 output を TF_VAR_<name>_OUTPUT の形式で export
for key in $(echo "$outputs_json" | jq -r 'keys[]'); do
  value=$(echo "$outputs_json" | jq -r ".\"$key\".value")
  # 環境変数名を小文字のまま TF_VAR_ を付与
  var_name="TF_VAR_${key}"
  export "$var_name=$value"
  echo "Exported $var_name=$value"
done

# ---------------------------------------------
# Docker イメージ push 後に digest を取得して export
# ---------------------------------------------
IMAGE_URL="${TF_VAR_region}-docker.pkg.dev/${TF_VAR_project_id}/${TF_VAR_artifact_repo_name}/${TF_VAR_image_name}"
# 最新イメージ digest を取得
DIGEST=$(gcloud artifacts docker images describe \
  "$IMAGE_URL:latest" --format="value(image_summary.digest)")
# 環境変数にセットして Terraform に渡す
export TF_VAR_image_digest="$DIGEST"
echo "Exported TF_VAR_image_digest=$DIGEST"