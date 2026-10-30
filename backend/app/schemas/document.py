import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import SummaryStatus, Visibility


class DocumentCreate(BaseModel):
    title: str
    authors: list[str] | None = None
    field: str | None = None
    keywords: list[str] | None = None
    visibility: Visibility = Visibility.PRIVATE


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    authors: list[str] | None
    field: str | None
    keywords: list[str] | None
    visibility: Visibility
    summary: str | None
    summary_status: SummaryStatus
    created_at: datetime


class DocumentListItem(BaseModel):
    """Slimmer shape for browse/search results — the front-page card."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    authors: list[str] | None
    field: str | None
    summary: str | None
    summary_status: SummaryStatus
    created_at: datetime
