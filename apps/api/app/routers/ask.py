from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.rag_service import answer_question

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    limit: int = 5


@router.post("/ask")
async def ask_question(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await answer_question(
            db=db,
            question=request.question,
            limit=request.limit,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error