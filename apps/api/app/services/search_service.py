from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


async def semantic_search(
    db: AsyncSession,
    query: str,
    limit: int = 5,
) -> list[DocumentChunk]:
    query_embedding = await generate_embedding(query)

    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
    )

    result = await db.execute(statement)

    return list(result.scalars().all())