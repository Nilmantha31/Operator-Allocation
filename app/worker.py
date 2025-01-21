from celery import Celery


celery_app = Celery('main')
celery_app.config_from_object("app.celeryconfig")

celery_app.autodiscover_tasks(['app.blueprints.opAutoAllocation_task'])


