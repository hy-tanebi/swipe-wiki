from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from swipe_wiki.db import get_db
from swipe_wiki.models import Article, Swipe
from swipe_wiki.schemas import ArticleOut, SwipeCreate, SwipeOut, WikiArticleOut

app = FastAPI()


@app.get("/articles", response_model=list[ArticleOut])
def get_articles(db: Session = Depends(get_db)):
    stmt = (
        select(Article)
        .outerjoin(Swipe, Swipe.article_id == Article.id)
        .where(Swipe.id.is_(None))
    )
    return db.execute(stmt).scalars().all()


@app.post("/swipes", response_model=SwipeOut, status_code=201)
def create_swipe(swipe_in: SwipeCreate, db: Session = Depends(get_db)):
    article = db.get(Article, swipe_in.article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="記事が取得できませんでした")

    existing = db.execute(
        select(Swipe).where(Swipe.article_id == swipe_in.article_id)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="すでに記事が存在しています")

    swipe = Swipe(article_id=swipe_in.article_id, decision=swipe_in.decision)
    db.add(swipe)
    db.commit()
    db.refresh(swipe)
    return swipe


@app.get("/wiki", response_model=list[WikiArticleOut])
def get_wiki(db: Session = Depends(get_db)):
    stmt = (
        select(Article, Swipe)
        .join(Swipe, Swipe.article_id == Article.id)
        .where(Swipe.decision == "keep")
        .order_by(Swipe.created_at.desc())
    )
    rows = db.execute(stmt).all()
    return [
        WikiArticleOut(
            id=article.id,
            title=article.title,
            url=article.url,
            tags=article.tags,
            published_at=article.published_at,
            source=article.source,
            saved_at=swipe.created_at,
        )
        for article, swipe in rows
    ]
