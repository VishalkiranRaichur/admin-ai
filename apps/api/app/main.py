from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import create_tables
from app.routers import documents, health


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router,
    prefix=settings.api_prefix,
    tags=["health"],
)

app.include_router(
    documents.router,
    prefix=f"{settings.api_prefix}/documents",
    tags=["documents"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "Admin AI API", "docs": "/docs"}