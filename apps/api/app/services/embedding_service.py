from openai import AsyncOpenAI

from app.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def get_openai_client() -> AsyncOpenAI:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_embedding(text: str) -> list[float]:
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("Cannot generate an embedding for empty text.")

    client = get_openai_client()

    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned_text,
        encoding_format="float",
    )

    return response.data[0].embedding


async def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    cleaned_texts = [
        text.strip()
        for text in texts
        if text.strip()
    ]

    if not cleaned_texts:
        raise ValueError(
            "Cannot generate embeddings for an empty list."
        )

    client = get_openai_client()

    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned_texts,
        encoding_format="float",
    )

    return [
        item.embedding
        for item in response.data
    ]