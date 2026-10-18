"""POST /swipes — 1件の記事に判定を保存する"""

import pytest
from sqlalchemy import select

from swipe_wiki.models import Swipe


@pytest.mark.parametrize("decision", ["keep", "drop"])
def test_判定を保存して201を返す(client, db_session, make_article, decision):
    article = make_article()

    response = client.post("/swipes", json={"article_id": article.id, "decision": decision})

    assert response.status_code == 201
    body = response.json()
    assert body["article_id"] == article.id
    assert body["decision"] == decision
    assert "created_at" in body

    saved = db_session.execute(select(Swipe)).scalars().all()
    assert [(s.article_id, s.decision) for s in saved] == [(article.id, decision)]


def test_存在しない記事は404(client):
    response = client.post("/swipes", json={"article_id": 9999, "decision": "keep"})

    assert response.status_code == 404
    assert response.json()["detail"] == "記事が取得できませんでした"


def test_同じ記事を2回判定すると409(client, make_article):
    article = make_article()
    client.post("/swipes", json={"article_id": article.id, "decision": "keep"})

    response = client.post("/swipes", json={"article_id": article.id, "decision": "drop"})

    assert response.status_code == 409
    assert response.json()["detail"] == "すでに記事が存在しています"


def test_keepとdrop以外の判定は422(client, make_article):
    article = make_article()

    response = client.post("/swipes", json={"article_id": article.id, "decision": "maybe"})

    assert response.status_code == 422
