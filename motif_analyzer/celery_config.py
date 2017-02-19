from __future__ import absolute_import
from celery import Celery


def make_celery(app):
    celery_app = Celery(
        __name__,
        broker=app.config['CELERY_BROKER_URL'],
        include=['motif_analyzer.tasks.analyze_sequence']
    )
    celery_app.conf.update(app.config)
    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery_app.Task = ContextTask
    return celery_app
