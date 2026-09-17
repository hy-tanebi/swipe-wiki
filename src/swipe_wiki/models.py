from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from swipe_wiki.db import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    url: Mapped[str] = mapped_column(unique=True)
    tags: Mapped[str | None]
    published_at: Mapped[datetime]
    source: Mapped[str]


class Swipe(Base):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), unique=True)
    decision: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
