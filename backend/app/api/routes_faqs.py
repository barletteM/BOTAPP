from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_bot_by_slug_or_404
from app.core.security import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQRead, FAQUpdate


router = APIRouter(prefix="/bots/{slug}/faqs", tags=["faqs"])


@router.get("", response_model=list[FAQRead])
def list_faqs(slug: str, db: Session = Depends(get_db), _: AdminUser = Depends(get_current_admin)) -> list[FAQ]:
    bot = get_bot_by_slug_or_404(db, slug)
    return list(db.scalars(select(FAQ).where(FAQ.bot_id == bot.id).order_by(FAQ.created_at.desc())).all())


@router.post("", response_model=FAQRead)
def create_faq(
    slug: str,
    payload: FAQCreate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> FAQ:
    bot = get_bot_by_slug_or_404(db, slug)
    faq = FAQ(bot_id=bot.id, question=payload.question, answer=payload.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.patch("/{faq_id}", response_model=FAQRead)
def update_faq(
    slug: str,
    faq_id: str,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> FAQ:
    bot = get_bot_by_slug_or_404(db, slug)
    faq = db.get(FAQ, faq_id)
    if not faq or faq.bot_id != bot.id:
        raise HTTPException(status_code=404, detail="FAQ not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(faq, field, value)
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}", status_code=204)
def delete_faq(
    slug: str,
    faq_id: str,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> None:
    bot = get_bot_by_slug_or_404(db, slug)
    faq = db.get(FAQ, faq_id)
    if not faq or faq.bot_id != bot.id:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(faq)
    db.commit()
