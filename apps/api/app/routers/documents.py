import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from openai import OpenAIError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.services.chunk_repository import save_chunks
from app.services.document_processor import process_document
from app.services.embedding_service import OpenAIConfigurationError
from app.services.storage import delete_file, upload_file

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md"}


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    try:
        result = await db.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())
    except SQLAlchemyError as error:
        logger.exception("Failed to list documents")
        raise HTTPException(
            status_code=503,
            detail="The document database is unavailable.",
        ) from error


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Document:
    filename = Path(file.filename or "unnamed").name

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

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if len(file_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_size_mb} MB upload limit.",
        )

    document_id = uuid.uuid4()

    storage_key = (
        f"documents/{document_id}/{filename}"
    )

    content_type = (
        file.content_type
        or "application/octet-stream"
    )

    document = Document(
        id=document_id,
        filename=filename,
        content_type=content_type,
        size_bytes=len(file_bytes),
        storage_key=storage_key,
        status="uploaded",
    )

    storage_uploaded = False

    try:
        await run_in_threadpool(
            upload_file,
            file_bytes,
            storage_key,
            content_type,
        )
        storage_uploaded = True

        result = await process_document(
            file_bytes,
            filename,
        )

        db.add(document)

        await save_chunks(
            db=db,
            document_id=document.id,
            chunks=result["chunks"],
            embeddings=result["embeddings"],
        )

        document.status = "processed"

        await db.commit()
        await db.refresh(document)

    except (OpenAIConfigurationError, OpenAIError, SQLAlchemyError, ValueError) as error:
        await db.rollback()

        if storage_uploaded:
            try:
                await run_in_threadpool(delete_file, storage_key)
            except Exception:
                logger.exception("Failed to clean up object %s", storage_key)

        logger.exception("Document processing failed for %s", filename)

        status_code = 502 if isinstance(error, OpenAIError) else 422
        if isinstance(error, OpenAIConfigurationError):
            status_code = 503
        if isinstance(error, SQLAlchemyError):
            status_code = 503

        raise HTTPException(
            status_code=status_code,
            detail=f"Document processing failed: {error}",
        ) from error
    except Exception as error:
        await db.rollback()

        if storage_uploaded:
            try:
                await run_in_threadpool(delete_file, storage_key)
            except Exception:
                logger.exception("Failed to clean up object %s", storage_key)

        logger.exception("Document upload failed for %s", filename)
        raise HTTPException(
            status_code=503,
            detail="Document storage is unavailable. Check the MinIO service.",
        ) from error

    return document
