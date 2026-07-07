from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bot import BotProfile


def get_bot_by_slug_or_404(db: Session, slug: str) -> BotProfile:
    bot = db.scalar(select(BotProfile).where(BotProfile.slug == slug))
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot
