"""initial schema: users, profiles, documents, document_embeddings, pgvector

Revision ID: 0001
Revises:
Create Date: 2026-10-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

EMBEDDING_DIM = 384  # matches app.core.config.Settings.embedding_dim; keep in sync


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Not created here with .create(): op.create_table() below creates each enum type
    # automatically the first time it's used as a column, so creating it twice would
    # fail with "type already exists".
    visibility_enum = postgresql.ENUM("public", "private", name="visibility")
    summary_status_enum = postgresql.ENUM("pending", "done", "failed", name="summarystatus")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_researcher_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("display_name", sa.String(255)),
        sa.Column("field_of_study", sa.String(255)),
        sa.Column("year_level", sa.String(50)),
        sa.Column("interests", postgresql.ARRAY(sa.String)),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("authors", postgresql.ARRAY(sa.String)),
        sa.Column("field", sa.String(255)),
        sa.Column("keywords", postgresql.ARRAY(sa.String)),
        sa.Column("visibility", visibility_enum, nullable=False, server_default="private"),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("extracted_text", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("summary_status", summary_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_documents_author_id", "documents", ["author_id"])
    op.create_index("ix_documents_visibility", "documents", ["visibility"])

    op.create_table(
        "document_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("vector", Vector(EMBEDDING_DIM), nullable=False),
    )
    # ivfflat speeds up cosine-similarity search once there are enough rows to train on;
    # harmless on an empty/small table, worth revisiting (lists count, or switch to HNSW) as data grows.
    op.execute(
        "CREATE INDEX ix_document_embeddings_vector ON document_embeddings "
        "USING ivfflat (vector vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_table("document_embeddings")
    op.drop_table("documents")
    op.drop_table("profiles")
    op.drop_table("users")
    sa.Enum(name="summarystatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="visibility").drop(op.get_bind(), checkfirst=True)
    op.execute("DROP EXTENSION IF EXISTS vector")
