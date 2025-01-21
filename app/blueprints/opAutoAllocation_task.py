from ..worker import celery_app

@celery_app.task()
def sum():
    return 5 + 10