from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_bot_by_slug_or_404
from app.core.security import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.chat import ChatSession
from app.schemas.chat import ChatSessionRead


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me")
def me(admin: AdminUser = Depends(get_current_admin)) -> dict[str, str]:
    return {"id": admin.id, "email": admin.email, "full_name": admin.full_name}


@router.get("/bots/{slug}/chat-history", response_model=list[ChatSessionRead])
def chat_history(
    slug: str,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
) -> list[ChatSession]:
    bot = get_bot_by_slug_or_404(db, slug)
    return list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.bot_id == bot.id)
            .options(selectinload(ChatSession.messages))
            .order_by(ChatSession.created_at.desc())
        ).all()
    )
