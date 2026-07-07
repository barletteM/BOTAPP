from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_bot_by_slug_or_404
from app.core.security import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.knowledge import KnowledgeDocument, KnowledgeVersion
from app.schemas.knowledge import KnowledgeDocumentRead, KnowledgeVersionRead, PastedKnowledgeCreate
from app.services.knowledge import add_document_version, add_text_knowledge, add_uploaded_knowledge


router = APIRouter(prefix="/bots/{slug}/knowledge", tags=["knowledge"])


@router.get("/documents", response_model=list[KnowledgeDocumentRead])
def list_documents(
    slug: str,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> list[KnowledgeDocument]:
    bot = get_bot_by_slug_or_404(db, slug)
    return list(
        db.scalars(
            select(KnowledgeDocument).where(KnowledgeDocument.bot_id == bot.id).order_by(KnowledgeDocument.created_at.desc())
        ).all()
    )


@router.get("/documents/{document_id}/versions", response_model=list[KnowledgeVersionRead])
def list_versions(
    slug: str,
    document_id: str,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> list[KnowledgeVersion]:
    bot = get_bot_by_slug_or_404(db, slug)
    document = db.get(KnowledgeDocument, document_id)
    if not document or document.bot_id != bot.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return list(
        db.scalars(
            select(KnowledgeVersion).where(KnowledgeVersion.document_id == document.id).order_by(KnowledgeVersion.version.desc())
        ).all()
    )


@router.post("/paste", response_model=KnowledgeDocumentRead)
def paste_knowledge(
    slug: str,
    payload: PastedKnowledgeCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> KnowledgeDocument:
    bot = get_bot_by_slug_or_404(db, slug)
    document = add_text_knowledge(
        db,
        bot_id=bot.id,
        title=payload.title,
        text=payload.text,
        source_type="manual_text",
        admin_id=admin.id,
        change_note=payload.change_note,
    )
    return document


@router.post("/upload", response_model=KnowledgeDocumentRead)
def upload_knowledge(
    slug: str,
    file: UploadFile = File(...),
    change_note: str = Form("Uploaded knowledge document"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> KnowledgeDocument:
    bot = get_bot_by_slug_or_404(db, slug)
    try:
        return add_uploaded_knowledge(
            db,
            bot_id=bot.id,
            bot_slug=bot.slug,
            file=file,
            admin_id=admin.id,
            change_note=change_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/documents/{document_id}/versions/paste", response_model=KnowledgeDocumentRead)
def paste_document_version(
    slug: str,
    document_id: str,
    payload: PastedKnowledgeCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
) -> KnowledgeDocument:
    bot = get_bot_by_slug_or_404(db, slug)
    document = db.get(KnowledgeDocument, document_id)
    if not document or document.bot_id != bot.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return add_document_version(
        db,
        document=document,
        bot_id=bot.id,
        text=payload.text,
        admin_id=admin.id,
        change_note=payload.change_note,
    )
