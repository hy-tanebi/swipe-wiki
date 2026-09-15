### GET /articles

概要:未判定の記事(swipesに判定がまだ無い記事)を、DBから取得する

送るもの: なし

返ってくるもの: DBのarticlesから未判定の記事

失敗した時: なし

認証: 不要

{
"id": 1,
"title": "FastAPI × PostgreSQLで…",
"url": "https://qiita.com/...",
"tags": "Python,FastAPI,PostgreSQL",
"published_at": "2026-09-14T10:00:00",
"source": "qiita"
}

### POST /swipes

概要: 1件の記事に判定の保存をする

送るもの: keep/drop 判定し、article_idと一緒に送る

返ってくるもの:今保存した判定そのもの(id, article_id, decision, created_at)

失敗した時: 存在しないarticle_idが該当したら404エラー出力（'記事が取得できませんでした'）。判定済みの記事がもう一度来たら409エラー出力('すでに記事が存在しています')

認証: 不要

{
"id": 1,
"article_id":1,
"decision":"keep",
"created_at": "2026-09-15T08:30:00"
}

### GET /wiki

概要: keep判定された記事をDBから取得する

送るもの: なし

返ってくるもの: swipesでkeep判定された記事

失敗した時: なし

認証: 不要

{
"id": 1,
"title": "FastAPI × PostgreSQLで…",
"url": "https://qiita.com/...",
"tags": "Python,FastAPI,PostgreSQL",
"published_at": "2026-09-14T10:00:00",
"source": "qiita",
"saved_at": "2026-09-15T08:30:00"
}
