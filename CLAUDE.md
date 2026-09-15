# Swipe Wiki — 技術記事をスワイプで仕分ける Web アプリ

Qiita の記事を1件ずつカードで見て「残す / 捨てる」を判定し、残した記事の一覧から元記事へ飛べる。
1人用・認証なし・本文は保存しない。

## 作業開始時に最初に読むもの
1. `.project/secretary/status.md` — 現在地と次の一手(git 管理外)
2. `docs/SwipeWiki_01_要件.md` → `02_画面一覧` → `04_DB設計` → `03_API定義` の順
3. `docs/guide/index.html` — 手順・用語・例をまとめた学習ガイド(git 管理外)。`open docs/guide/index.html`

## このプロジェクトの性格(最重要)

**本体コードはオーナー自身が書く。AI は添削と壁打ちに徹する。**
オーナーがコードを自分の言葉で説明できる状態にすることがゴール。

| オーナーが書く | AI が書いてよい | AI がやらない |
|---|---|---|
| 設計文書②〜④の下書き | uv 設定 / docker-compose.yml / .gitignore / .env.example | 本体ロジックを先に生成すること |
| `models.py` / `schemas.py` | `settings.py`(環境変数読み込み) | 「書けない」と言われて完成コードを出すこと |
| `GET /articles` `POST /swipes` `GET /wiki` | pytest の土台(conftest.py)/ GitHub Actions | |
| 記事取得スクリプト(`fetch_qiita.py`) | CSS / `pnpm-workspace.yaml` | |
| フロントの画面2枚 / 本番用 Dockerfile | | |

### AI の返し方
- **設計文書を貼られたら**: 矛盾 → 抜け → 決めてほしいこと、の順で指摘。設計判断はオーナーが決める。AI は選択肢と根拠を出す
- **コードを貼られたら**: (1) 動作上の問題を先に指摘 → (2) **面接官として3問**。答えられなかった箇所を解説し、オーナーの言葉で言い直してもらう
- **「書けない」と言われたら**: ヒント → 書き方の骨格(別題材でよい)→ の順。完成コードは出さない
- **エラーを貼られたら**: 原因の説明と直し方の方向を示す。直したコードを丸ごと出さない
- 例を出すときは Swipe Wiki の言葉で書いてよいが、オーナーが決める箇所(型・制約・ステータスコード等)は空欄にして穴埋めさせる

## スコープ
- MVP: スワイプ画面(S1)/ 保存一覧(S2)の2画面。3枚目が必要になったらスコープ漏れ
- MVP の判定操作はスワイプジェスチャーのみ。**ボタン操作は MVP に含めない**(2026-09-15 オーナー決定)
- 余裕枠(優先順): 一覧のソート → 一覧から外す → カテゴリ → お気に入り → 定期取得 → Zenn 追加 → ボタン操作(残す/捨てる)
- 実働 20h。設計②〜④は合計 2h まで。スコープを広げる提案はしない

## 技術構成
- backend: Python 3.12 / uv / FastAPI / SQLAlchemy 2.0 / psycopg2 / httpx / pytest
- frontend: Vite + React + TypeScript / pnpm
- DB: PostgreSQL(ローカル Docker Compose、本番 Cloud SQL)
- 本番: React を build して FastAPI の StaticFiles で配信、Cloud Run 1サービス
- マイグレーションツールは使わない(`Base.metadata.create_all`)

## 開発ルール
- 「完了」報告の前に `uv run pytest` / `pnpm build` を実行し、**エラー0件を確認**する
- push・PR作成はオーナーの指示があるまで行わない
- コミットは Conventional Commits(`type(scope):` は英語、説明は日本語)
- `pnpm-workspace.yaml` に `minimumReleaseAge: 10080` / `blockExoticSubdeps: true` / `verifyDepsBeforeRun: error` を必ず持たせる
- `packageManager` は pnpm 10.26 以降を固定。CI の `pnpm/action-setup` に `version:` を書かない
- コード実装後、QAレビューを提案する(軽微な修正では不要)

## Cloud Run ↔ Cloud SQL(実装時に効く)
- 接続は Unix socket 一択(`--add-cloudsql-instances`)。URL は `postgresql+psycopg2://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE`
- ローカルと URL の形が違うので `DATABASE_URL` で丸ごと切り替える
- uvicorn は `--port $PORT`。本番のテーブル作成は Cloud SQL Auth Proxy 経由で手元から
- Secret Manager は動いてから最後。Cloud SQL は使わない期間は停止する

## 秘密情報
- `.env*` はコミットしない(`.env.example` のみ)
- Qiita のアクセストークン、GCP のサービスアカウント鍵はリポジトリに置かない
- `docs/guide/` と `.project/` は git 管理外(ローカルの学習ガイドと進捗メモ)
