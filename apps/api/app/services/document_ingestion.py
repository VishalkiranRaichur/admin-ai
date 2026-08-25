from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document
from app.services.chunk_repository import save_chunks

UploadAdapter = Callable[[bytes, str, str], str]
DeleteAdapter = Callable[[str], None]
ProcessorAdapter = Callable[[bytes, str], Awaitable[dict]]


async def ingest_document(
    *,
    db: AsyncSession,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    storage_key: str,
    upload: UploadAdapter,
    delete: DeleteAdapter,
    processor: ProcessorAdapter,
    document_id: uuid.UUID | None = None,
    commit: bool = True,
) -> Document:
    """Store, parse, chunk, embed, and persist a document without HTTP concerns."""
    document = Document(
        id=document_id or uuid.uuid4(),
        filename=filename,
        content_type=content_type,
        size_bytes=len(file_bytes),
        storage_key=storage_key,
        status="uploaded",
    )
    storage_uploaded = False
    try:
        await __import__("asyncio").to_thread(upload, file_bytes, storage_key, content_type)
        storage_uploaded = True
        result = await processor(file_bytes, filename)
        db.add(document)
        await save_chunks(
            db=db,
            document_id=document.id,
            chunks=result["chunks"],
            embeddings=result["embeddings"],
        )
        document.status = "processed"
        if commit:
            await db.commit()
            await db.refresh(document)
        else:
            await db.flush()
        return document
    except Exception:
        await db.rollback()
        if storage_uploaded:
            try:
                await __import__("asyncio").to_thread(delete, storage_key)
            except Exception:
                pass
        raise
