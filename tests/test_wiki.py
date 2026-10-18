"""GET /wiki — keep 判定された記事を、保存した新しい順に返す"""

from datetime import datetime


def test_keepの記事だけを返す(client, make_article, make_swipe):
    kept = make_article()
    dropped = make_article()
    make_article()  # 未判定
    make_swipe(kept, "keep")
    make_swipe(dropped, "drop")

    response = client.get("/wiki")

    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == [kept.id]


def test_保存した日時の新しい順に並ぶ(client, make_article, make_swipe):
    old = make_article()
    new = make_article()
    make_swipe(old, "keep", created_at=datetime(2026, 9, 15, 8, 0, 0))
    make_swipe(new, "keep", created_at=datetime(2026, 9, 16, 8, 0, 0))

    response = client.get("/wiki")

    assert [a["id"] for a in response.json()] == [new.id, old.id]


def test_保存日時をsaved_atとして返す(client, make_article, make_swipe):
    article = make_article()
    make_swipe(article, "keep", created_at=datetime(2026, 9, 15, 8, 30, 0))

    item = client.get("/wiki").json()[0]

    assert set(item) == {"id", "title", "url", "tags", "published_at", "source", "saved_at"}
    assert item["saved_at"] == "2026-09-15T08:30:00"
