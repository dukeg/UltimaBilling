from celery import Celery
from ..core.config import settings

celery = Celery("billing", broker=settings.redis_url, backend=settings.redis_url, include=["app.workers.tasks"])
celery.conf.beat_schedule = {
    "generate-recurring-invoices-hourly": {"task": "app.workers.tasks.generate_recurring_invoices", "schedule": 3600},
    "mark-overdue-invoices-daily": {"task": "app.workers.tasks.mark_overdue_invoices", "schedule": 86400},
}
