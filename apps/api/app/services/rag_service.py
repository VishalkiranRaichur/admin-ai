from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.openai_client import get_openai_client
from app.services.search_service import semantic_search


async def answer_question(
    db: AsyncSession,
    question: str,
    limit: int = 5,
) -> dict:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    chunks = await semantic_search(
        db=db,
        query=cleaned_question,
        limit=limit,
    )

    if not chunks:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(
        chunk.content
        for chunk in chunks
    )

    prompt = f"""
You are Admin AI.

Answer the user's question using only the provided document context.

If the answer is not supported by the context,
say that you could not find enough information in the uploaded documents.

Do not invent facts.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{cleaned_question}
"""

    client = get_openai_client()

    response = await client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content or ""

    return {
        "answer": answer,
        "sources": [
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
    }
