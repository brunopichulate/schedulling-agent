from celery import Celery
from src.core.config import settings

celery_app = Celery("endeavor_ai")

celery_app.conf.update(
  broker_url=settings.redis.URL,
  result_backend=settings.redis.URL,
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="UTC",
  enable_utc=True,
)

# Auto-discover tasks in the src/tasks directory
celery_app.autodiscover_tasks(["src.tasks.whatsapp"])
