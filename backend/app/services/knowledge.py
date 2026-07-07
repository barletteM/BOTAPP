from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeVersion
from app.services.document_parser import parse_document
from app.services.embeddings import embed_texts


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 180) -> list[str]:
    clean = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def add_text_knowledge(
    db: Session,
    *,
    bot_id: str,
    title: str,
    text: str,
    source_type: str,
    file_name: str = "",
    storage_path: str = "",
    admin_id: str | None = None,
    change_note: str = "",
) -> KnowledgeDocument:
    content_hash = sha256(text.encode("utf-8")).hexdigest()
    document = KnowledgeDocument(
        bot_id=bot_id,
        title=title,
        source_type=source_type,
        file_name=file_name,
        storage_path=storage_path,
        current_version=1,
    )
    db.add(document)
    db.flush()
    version = KnowledgeVersion(
        document_id=document.id,
        version=1,
        content_hash=content_hash,
        change_note=change_note,
        created_by_admin_id=admin_id,
    )
    db.add(version)
    db.flush()

    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    for index, chunk in enumerate(chunks):
        db.add(
            KnowledgeChunk(
                bot_id=bot_id,
                version_id=version.id,
                content=chunk,
                chunk_index=index,
                embedding=embeddings[index],
            )
        )
    db.commit()
    db.refresh(document)
    return document


def add_document_version(
    db: Session,
    *,
    document: KnowledgeDocument,
    bot_id: str,
    text: str,
    admin_id: str | None,
    change_note: str,
) -> KnowledgeDocument:
    content_hash = sha256(text.encode("utf-8")).hexdigest()
    next_version = document.current_version + 1
    version = KnowledgeVersion(
        document_id=document.id,
        version=next_version,
        content_hash=content_hash,
        change_note=change_note,
        created_by_admin_id=admin_id,
    )
    db.add(version)
    db.flush()
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    for index, chunk in enumerate(chunks):
        db.add(
            KnowledgeChunk(
                bot_id=bot_id,
                version_id=version.id,
                content=chunk,
                chunk_index=index,
                embedding=embeddings[index],
            )
        )
    document.current_version = next_version
    db.commit()
    db.refresh(document)
    return document


def save_upload(file: UploadFile, bot_slug: str) -> Path:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir) / bot_slug
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload.txt").name
    destination = upload_dir / f"{uuid4()}-{safe_name}"
    with destination.open("wb") as buffer:
        while data := file.file.read(1024 * 1024):
            buffer.write(data)
    return destination


def add_uploaded_knowledge(
    db: Session,
    *,
    bot_id: str,
    bot_slug: str,
    file: UploadFile,
    admin_id: str | None,
    change_note: str,
) -> KnowledgeDocument:
    path = save_upload(file, bot_slug)
    text = parse_document(path)
    if not text:
        raise ValueError("No readable text was found in the uploaded document.")
    return add_text_knowledge(
        db,
        bot_id=bot_id,
        title=Path(file.filename or path.name).stem,
        text=text,
        source_type=path.suffix.lower().replace(".", ""),
        file_name=file.filename or path.name,
        storage_path=str(path),
        admin_id=admin_id,
        change_note=change_note,
    )


def list_current_chunks(db: Session, bot_id: str) -> list[KnowledgeChunk]:
    documents = db.scalars(select(KnowledgeDocument).where(KnowledgeDocument.bot_id == bot_id)).all()
    version_ids = []
    for document in documents:
        version = db.scalar(
            select(KnowledgeVersion)
            .where(KnowledgeVersion.document_id == document.id)
            .order_by(KnowledgeVersion.version.desc())
        )
        if version:
            version_ids.append(version.id)
    if not version_ids:
        return []
    return db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.version_id.in_(version_ids))).all()
