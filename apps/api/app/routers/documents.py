import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.services.chunk_repository import save_chunks
from app.services.document_processor import process_document
from app.services.storage import upload_file

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md"}


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Document:
    filename = file.filename or "unnamed"

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    document_id = uuid.uuid4()

    storage_key = (
        f"documents/{document_id}/{filename}"
    )

    content_type = (
        file.content_type
        or "application/octet-stream"
    )

    upload_file(
        file_bytes=file_bytes,
        storage_key=storage_key,
        content_type=content_type,
    )

    document = Document(
        id=document_id,
        filename=filename,
        content_type=content_type,
        size_bytes=len(file_bytes),
        storage_key=storage_key,
        status="uploaded",
    )

    try:
        result = process_document(
            file_bytes,
            filename,
        )

        db.add(document)

        await save_chunks(
            db=db,
            document_id=document.id,
            chunks=result["chunks"],
        )

        document.status = "processed"

        await db.commit()
        await db.refresh(document)

    except Exception as error:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {error}",
        ) from error

    return document