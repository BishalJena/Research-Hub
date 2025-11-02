from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "research_hub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "app.tasks.literature_review.*": {"queue": "literature_review"},
    "app.tasks.plagiarism.*": {"queue": "plagiarism"},
    "app.tasks.journal_recommendation.*": {"queue": "journal_recommendation"},
}
