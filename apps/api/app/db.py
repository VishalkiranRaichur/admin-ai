"""Database models and session — expanded in Phase 1."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def create_tables() -> None:
    from app.models import Document  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)