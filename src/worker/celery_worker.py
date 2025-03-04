from celery import Celery
from src.config.settings import setting

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker=setting.CELERY_BROKER_URL,   # RabbitMQ broker
    backend=setting.CELERY_RESULT_BACKEND,  # Redis result backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

# Auto-discover tasks from modules
celery_app.autodiscover_tasks(["src.app.plc_module.tasks"])

# Celery Beat (Periodic Tasks)
celery_app.conf.beat_schedule = {
    "fetch-plc-messages-every-5-seconds": {
        "task": "src.app.plc_module.tasks.fetch_plc_messages",
        "schedule": 5.0,
    },
    "fetch-multiple-plcs-every-second": {
        "task": "src.app.plc_module.tasks.fetch_all_plc_messages",
        "schedule": 1.0,
    },
}

if __name__ == "__main__":
    celery_app.start()
