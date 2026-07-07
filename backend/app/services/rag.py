from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import get_settings
from app.models.bot import BotProfile
from app.models.chat import ChatMessage, ChatSession
from app.models.faq import FAQ
from app.models.knowledge import KnowledgeChunk
from app.services.embeddings import embed_texts
from app.services.knowledge import list_current_chunks


FALLBACK = "I do not have confirmed information about that. Please contact the office directly."


def _keyword_score(query: str, text: str) -> int:
    terms = {term.lower().strip(".,?!") for term in query.split() if len(term) > 2}
    haystack = text.lower()
    return sum(1 for term in terms if term in haystack)


def retrieve_context(db: Session, bot_id: str, question: str, limit: int = 5) -> list[str]:
    settings = get_settings()
    chunks = list_current_chunks(db, bot_id)
    faqs = db.scalars(select(FAQ).where(FAQ.bot_id == bot_id)).all()
    faq_contexts = [f"FAQ Question: {faq.question}\nFAQ Answer: {faq.answer}" for faq in faqs]

    if settings.openai_api_key and settings.database_url.startswith("postgresql") and chunks and any(chunk.embedding is not None for chunk in chunks):
        query_embedding = embed_texts([question])[0]
        if query_embedding is not None:
            vector_rows = db.scalars(
                select(KnowledgeChunk)
                .where(KnowledgeChunk.bot_id == bot_id, KnowledgeChunk.embedding.is_not(None))
                .order_by(KnowledgeChunk.embedding.cosine_distance(query_embedding))
                .limit(limit)
            ).all()
            return faq_contexts[:2] + [row.content for row in vector_rows]

    scored = [(context, _keyword_score(question, context)) for context in faq_contexts]
    scored.extend((chunk.content, _keyword_score(question, chunk.content)) for chunk in chunks)
    return [text for text, score in sorted(scored, key=lambda item: item[1], reverse=True)[:limit] if score > 0]


def answer_question(db: Session, *, bot: BotProfile, message: str, session_id: str | None, visitor_name: str) -> tuple[str, str]:
    session = db.get(ChatSession, session_id) if session_id else None
    if not session or session.bot_id != bot.id:
        session = ChatSession(bot_id=bot.id, visitor_name=visitor_name)
        db.add(session)
        db.flush()

    db.add(ChatMessage(session_id=session.id, role="user", content=message))
    contexts = retrieve_context(db, bot.id, message)
    if not contexts:
        answer = FALLBACK
    else:
        answer = _generate_answer(bot, message, contexts)
    db.add(ChatMessage(session_id=session.id, role="assistant", content=answer))
    db.commit()
    return session.id, answer


def _generate_answer(bot: BotProfile, question: str, contexts: list[str]) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        joined = "\n\n".join(contexts[:2])
        return f"{joined[:700]}\n\nFor anything else, please contact the office directly."

    client = OpenAI(api_key=settings.openai_api_key)
    system = (
        "You are a professional receptionist. Answer briefly and politely. "
        "Use only the approved context for this exact bot. "
        f"If the answer is not clearly in context, say exactly: {FALLBACK}\n\n"
        f"Bot: {bot.name}\nInstructions: {bot.reception_instructions}"
    )
    user = f"Approved context:\n{chr(10).join(contexts)}\n\nVisitor question: {question}"
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=220,
    )
    return response.choices[0].message.content or FALLBACK
