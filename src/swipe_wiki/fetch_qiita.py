from datetime import datetime

import httpx
from sqlalchemy import select

from swipe_wiki.db import SessionLocal
from swipe_wiki.models import Article
from swipe_wiki.settings import settings

QIITA_API_URL = "https://qiita.com/api/v2/items"


def fetch_qiita_items(per_page: int = 20) -> list[dict]:
    headers = {}
    if settings.QIITA_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {settings.QIITA_ACCESS_TOKEN}"

    response = httpx.get(QIITA_API_URL, params={"per_page": per_page}, headers=headers)
    response.raise_for_status()
    return response.json()


def save_articles(items: list[dict]) -> int:
    session = SessionLocal()
    try:
        urls = [item["url"] for item in items]
        existing_urls = {
            row[0]
            for row in session.execute(select(Article.url).where(Article.url.in_(urls))).all()
        }

        new_articles = [
            Article(
                title=item["title"],
                url=item["url"],
                tags=",".join(tag["name"] for tag in item["tags"]) or None,
                published_at=datetime.fromisoformat(item["created_at"]),
                source="qiita",
            )
            for item in items
            if item["url"] not in existing_urls
        ]

        session.add_all(new_articles)
        session.commit()
        return len(new_articles)
    finally:
        session.close()


if __name__ == "__main__":
    items = fetch_qiita_items()
    saved_count = save_articles(items)
    print(f"{len(items)}件中{saved_count}件保存しました")
