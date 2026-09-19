# ---- 1. フロントをビルドする ----
FROM node:22-slim AS frontend-build
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@10.34.5 --activate

COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY frontend/package.json frontend/package.json
RUN pnpm install --frozen-lockfile

COPY frontend/ frontend/
RUN pnpm --filter frontend build


# ---- 2. バックエンド + ビルド済みフロントを1つにまとめる ----
FROM python:3.12-slim AS backend

# psycopg2(ソースからビルドする版)に必要なコンパイラとPostgresヘッダ
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev

COPY --from=frontend-build /app/frontend/dist/ src/swipe_wiki/static/

ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8080
CMD ["sh", "-c", "uvicorn swipe_wiki.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
