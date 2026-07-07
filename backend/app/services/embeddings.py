from openai import OpenAI

from app.core.config import get_settings


def embed_texts(texts: list[str]) -> list[list[float] | None]:
    settings = get_settings()
    if not settings.openai_api_key:
        return [None for _ in texts]
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]
