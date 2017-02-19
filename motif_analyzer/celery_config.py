from celery import Celery


def make_celery(app):
    celery_tasks = '.'.join([app.import_name, 'celery_tasks'])
    print('%s' % celery_tasks)
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        include=[celery_tasks]
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery