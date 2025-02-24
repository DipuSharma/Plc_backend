from celery import Celery
from src.config.settings import setting

# Create Celery app
celery_app = Celery(
    "worker",
    broker=setting.CELERY_BROKER_URL,
    backend=setting.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

# Define periodic tasks using Celery Beat
celery_app.conf.beat_schedule = {
    "delete-inactive-companies": {
        "task": "src.app.plc_module.tasks.fetch_plc_messages",
        "schedule": 5.0,
    },
    "fetch-multiple-plcs-every-second": {
        "task": "src.app.plc_module.tasks.fetch_all_plc_messages",
        "schedule": 1.0,  # Every second
    },
}

# Load tasks from all modules in the application
celery_app.autodiscover_tasks(
    [
        "src.app.plc_module.tasks",
    ]
)
