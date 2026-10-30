import uuid
from datetime import datetime
from enum import Enum as PyEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.core.database import Base

settings = get_settings()


class Visibility(str, PyEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class SummaryStatus(str, PyEnum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    field: Mapped[str | None] = mapped_column(String(255))
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    visibility: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name="visibility", values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=Visibility.PRIVATE,
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text)

    summary: Mapped[str | None] = mapped_column(Text)
    summary_status: Mapped[SummaryStatus] = mapped_column(
        Enum(
            SummaryStatus,
            name="summarystatus",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=SummaryStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped["User"] = relationship(back_populates="documents")
    embedding: Mapped["DocumentEmbedding"] = relationship(
        back_populates="document", uselist=False, cascade="all, delete-orphan"
    )


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim), nullable=False)

    document: Mapped["Document"] = relationship(back_populates="embedding")
