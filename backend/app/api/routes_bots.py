from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_bot_by_slug_or_404
from app.core.security import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.bot import BotProfile
from app.schemas.bot import BotProfileRead, BotProfileUpdate
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import answer_question


router = APIRouter(prefix="/bots", tags=["bots"])


@router.get("", response_model=list[BotProfileRead])
def list_bots(db: Session = Depends(get_db)) -> list[BotProfile]:
    return list(db.scalars(select(BotProfile).order_by(BotProfile.name)).all())


@router.get("/{slug}", response_model=BotProfileRead)
def read_bot(slug: str, db: Session = Depends(get_db)) -> BotProfile:
    return get_bot_by_slug_or_404(db, slug)


@router.patch("/{slug}", response_model=BotProfileRead)
def update_bot(
    slug: str,
    payload: BotProfileUpdate,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> BotProfile:
    bot = get_bot_by_slug_or_404(db, slug)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bot, field, value)
    db.commit()
    db.refresh(bot)
    return bot


@router.post("/{slug}/chat", response_model=ChatResponse)
def chat(slug: str, payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    bot = get_bot_by_slug_or_404(db, slug)
    session_id, answer = answer_question(
        db,
        bot=bot,
        message=payload.message,
        session_id=payload.session_id,
        visitor_name=payload.visitor_name,
    )
    return ChatResponse(session_id=session_id, answer=answer)
