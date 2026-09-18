from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Decision = Literal["keep", "drop"]


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    tags: str | None
    published_at: datetime
    source: str


class SwipeCreate(BaseModel):
    article_id: int
    decision: Decision


class SwipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    decision: Decision
    created_at: datetime


class WikiArticleOut(BaseModel):
    id: int
    title: str
    url: str
    tags: str | None
    published_at: datetime
    source: str
    saved_at: datetime
