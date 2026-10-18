"""テストの土台。

- 開発用DBとは別の「テスト用DB」(名前が _test で終わるDB)を使う
- テスト開始時にテーブルを作り直し、テスト1件ごとに中身を空にする
- アプリの get_db と、fetch_qiita が直接使う SessionLocal をテスト用DBに差し替える
"""

import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url, text
from sqlalchemy.orm import sessionmaker

from swipe_wiki import fetch_qiita
from swipe_wiki.db import Base, get_db
from swipe_wiki.main import app
from swipe_wiki.models import Article, Swipe
from swipe_wiki.settings import settings


def _test_database_url() -> str:
    # CI では TEST_DATABASE_URL を渡す。ローカルでは .env の DATABASE_URL の DB名に _test を付ける
    if url := os.environ.get("TEST_DATABASE_URL"):
        return url
    base = make_url(settings.DATABASE_URL)
    return base.set(database=f"{base.database}_test").render_as_string(hide_password=False)


TEST_DATABASE_URL = _test_database_url()

# 開発用DBのデータを消さないための安全装置
if not make_url(TEST_DATABASE_URL).database.endswith("_test"):
    raise RuntimeError("テスト用DBの名前は _test で終わる必要があります")

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)


def _create_database_if_missing() -> None:
    # CREATE DATABASE はトランザクション内で実行できないので AUTOCOMMIT で接続する
    url = make_url(TEST_DATABASE_URL)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    _create_database_if_missing()
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield
    test_engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE swipes, articles RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def _use_test_session(monkeypatch):
    # fetch_qiita は get_db を通らず SessionLocal を直接使うため、こちらも差し替える
    monkeypatch.setattr(fetch_qiita, "SessionLocal", TestSessionLocal)


@pytest.fixture
def db_session():
    """テストの前提データを入れたり、APIを呼んだ後のDBを確認したりするためのセッション。"""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def make_article(db_session):
    """記事を1件DBに入れて返す。URL は重複しないよう連番にする。"""
    counter = 0

    def _make(**overrides) -> Article:
        nonlocal counter
        counter += 1
        values = {
            "title": f"記事{counter}",
            "url": f"https://qiita.com/test/items/{counter}",
            "tags": "Python,FastAPI",
            "published_at": datetime(2026, 9, 14, 10, 0, 0),
            "source": "qiita",
        }
        article = Article(**(values | overrides))
        db_session.add(article)
        db_session.commit()
        return article

    return _make


@pytest.fixture
def make_swipe(db_session):
    """判定を1件DBに入れて返す。created_at を指定すると保存日時を固定できる。"""

    def _make(article: Article, decision: str, **overrides) -> Swipe:
        swipe = Swipe(article_id=article.id, decision=decision, **overrides)
        db_session.add(swipe)
        db_session.commit()
        return swipe

    return _make


@pytest.fixture
def client():
    """APIを呼ぶためのクライアント。DBはテスト用DBにつながる。"""

    def _override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
