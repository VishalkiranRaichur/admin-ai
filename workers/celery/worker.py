"""Celery application foundation for durable ORION investigation work."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "orion",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    task_soft_time_limit=settings.investigation_max_runtime_seconds,
    task_time_limit=settings.investigation_max_runtime_seconds + 30,
    task_track_started=True,
    timezone="UTC",
)

# Investigation tasks are intentionally added in Phase 4.
