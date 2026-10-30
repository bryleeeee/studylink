import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.document import Document, Visibility
from app.models.user import User
from app.schemas.document import DocumentListItem, DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def _extract_text(file_path: Path) -> str:
    """Pull plain text out of a PDF. Returns an empty string if extraction fails
    (e.g. a scanned, image-only PDF) rather than raising, so upload still succeeds;
    summary_status stays PENDING until the Phase 2 pipeline retries or flags it."""
    try:
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    title: str = Form(...),
    authors: str | None = Form(None),  # comma-separated in the form, split below
    field: str | None = Form(None),
    keywords: str | None = Form(None),  # comma-separated
    visibility: Visibility = Form(Visibility.PRIVATE),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4()
    file_path = upload_dir / f"{doc_id}.pdf"
    contents = file.file.read()
    file_path.write_bytes(contents)

    extracted_text = _extract_text(file_path)

    document = Document(
        id=doc_id,
        author_id=current_user.id,
        title=title,
        authors=[a.strip() for a in authors.split(",")] if authors else None,
        field=field,
        keywords=[k.strip() for k in keywords.split(",")] if keywords else None,
        visibility=visibility,
        file_path=str(file_path),
        extracted_text=extracted_text or None,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Phase 2 hooks into here: enqueue summary + embedding generation for `document.id`.
    return document


@router.get("", response_model=list[DocumentListItem])
def browse_documents(
    q: str | None = None,
    field: str | None = None,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> list[Document]:
    """Keyword browse/search for Phase 1. Semantic search is added in Phase 2
    as a separate endpoint (e.g. /documents/search/semantic) so this one stays simple."""
    stmt = select(Document).where(Document.visibility == Visibility.PUBLIC)
    if current_user is not None:
        # Authors also see their own private documents mixed into results.
        stmt = select(Document).where(
            (Document.visibility == Visibility.PUBLIC) | (Document.author_id == current_user.id)
        )
    if q:
        stmt = stmt.where(Document.title.ilike(f"%{q}%"))
    if field:
        stmt = stmt.where(Document.field == field)
    stmt = stmt.order_by(Document.created_at.desc())
    return list(db.scalars(stmt))


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    is_owner = current_user is not None and document.author_id == current_user.id
    if document.visibility == Visibility.PRIVATE and not is_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
