from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


async def save_chunks(
    db: AsyncSession,
    document_id: UUID,
    chunks: list[str],
) -> list[DocumentChunk]:
    chunk_objects = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
        )
        for index, chunk in enumerate(chunks)
    ]

    db.add_all(chunk_objects)

    return chunk_objects