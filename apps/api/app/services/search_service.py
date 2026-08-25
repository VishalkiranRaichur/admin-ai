from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


async def semantic_search(
    db: AsyncSession,
    query: str,
    limit: int = 5,
    document_ids: list[UUID] | None = None,
) -> list[DocumentChunk]:
    query_embedding = await generate_embedding(query)

    statement = (
        select(DocumentChunk)
        .options(joinedload(DocumentChunk.document))
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
    )
    if document_ids:
        statement = statement.where(DocumentChunk.document_id.in_(document_ids))
    statement = statement.limit(limit)

    result = await db.execute(statement)

    return list(result.scalars().all())
