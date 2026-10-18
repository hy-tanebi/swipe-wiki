"""GET /articles — 未判定の記事だけを返す"""


def test_記事が無ければ空の配列を返す(client):
    response = client.get("/articles")

    assert response.status_code == 200
    assert response.json() == []


def test_判定済みの記事は返さない(client, make_article, make_swipe):
    unswiped = make_article()
    kept = make_article()
    dropped = make_article()
    make_swipe(kept, "keep")
    make_swipe(dropped, "drop")

    response = client.get("/articles")

    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == [unswiped.id]


def test_API定義どおりの項目を返す(client, make_article):
    make_article(title="FastAPI入門", tags=None)

    article = client.get("/articles").json()[0]

    assert set(article) == {"id", "title", "url", "tags", "published_at", "source"}
    assert article["title"] == "FastAPI入門"
    assert article["tags"] is None
