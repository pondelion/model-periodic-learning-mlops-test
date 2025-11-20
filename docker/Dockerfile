# ベースイメージ
FROM ghcr.io/astral-sh/uv:0.9.2-python3.12-bookworm-slim

# 環境変数設定（PythonのバッファリングOFF、pipのキャッシュ抑制）
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 作業ディレクトリ
WORKDIR /app

# pyproject.toml と lock ファイルをコピーして依存をインストール
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# mplm パッケージのみコピーして editable インストール
COPY mplm ./mplm
RUN uv pip install -e .

# Cloud Run 実行時に main.py を起動
CMD ["uv", "run", "python", "mplm/main.py"]