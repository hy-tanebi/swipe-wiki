"""POST /articles/fetch — Qiita から取得し、DB にまだ無い記事だけを保存する

本物の Qiita には接続しない。fetch_qiita_items を偽物に差し替えて、
「Qiita がこう返したら、アプリはこう動く」を確かめる。
"""

import httpx
import pytest
from sqlalchemy import select

from swipe_wiki import fetch_qiita
from swipe_wiki.models import Article


def qiita_item(n: int, tags: list[str] | None = None) -> dict:
    """Qiita API が返す記事1件の形(使う項目だけ)"""
    return {
        "title": f"Qiita記事{n}",
        "url": f"https://qiita.com/test/items/q{n}",
        "tags": [{"name": t} for t in (tags if tags is not None else ["Python"])],
        "created_at": "2026-09-14T10:00:00+09:00",
    }


@pytest.fixture
def fake_qiita(monkeypatch):
    """ページ番号ごとに返す記事を決めておける、偽物の Qiita。呼ばれたページを記録する。"""
    pages: dict[int, list[dict]] = {}
    called_pages: list[int] = []

    def _fake(per_page: int = 20, page: int = 1) -> list[dict]:
        called_pages.append(page)
        return pages.get(page, [])

    monkeypatch.setattr(fetch_qiita, "fetch_qiita_items", _fake)
    return pages, called_pages


def test_新しい記事を保存して件数を返す(client, db_session, fake_qiita):
    pages, _ = fake_qiita
    pages[1] = [qiita_item(1, tags=["Python", "FastAPI"]), qiita_item(2, tags=[])]

    response = client.post("/articles/fetch")

    assert response.status_code == 200
    assert response.json() == {"fetched": 2, "saved": 2}

    articles = db_session.execute(select(Article).order_by(Article.url)).scalars().all()
    assert [(a.title, a.tags, a.source) for a in articles] == [
        ("Qiita記事1", "Python,FastAPI", "qiita"),
        ("Qiita記事2", None, "qiita"),  # タグが無ければ None
    ]


def test_DBにある記事は保存しない(client, make_article, fake_qiita):
    pages, _ = fake_qiita
    make_article(url=qiita_item(1)["url"])
    pages[1] = [qiita_item(1), qiita_item(2)]

    response = client.post("/articles/fetch")

    assert response.json() == {"fetched": 2, "saved": 1}


def test_1ページ目が全部重複なら次のページまで遡る(client, make_article, fake_qiita):
    pages, called_pages = fake_qiita
    pages[1] = [qiita_item(n) for n in range(1, 21)]  # 20件ちょうど = まだ続きがある
    for item in pages[1]:
        make_article(url=item["url"])
    pages[2] = [qiita_item(21)]

    response = client.post("/articles/fetch")

    assert response.json() == {"fetched": 21, "saved": 1}
    assert called_pages == [1, 2]


def test_新しい記事が見つかったらそこで止まる(client, fake_qiita):
    pages, called_pages = fake_qiita
    pages[1] = [qiita_item(n) for n in range(1, 21)]

    client.post("/articles/fetch")

    assert called_pages == [1]


def test_Qiitaにつながらなければ502(client, monkeypatch):
    def _fail(**kwargs):
        raise httpx.ConnectError("接続できない")

    monkeypatch.setattr(fetch_qiita, "fetch_qiita_items", _fail)

    response = client.post("/articles/fetch")

    assert response.status_code == 502
    assert response.json()["detail"] == "Qiitaから記事を取得できませんでした"
