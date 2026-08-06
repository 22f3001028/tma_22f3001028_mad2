from flask import Flask
from celery import Celery
from celery.schedules import crontab
from config import Config
from extensions import db, jwt, mail


def create_flask_app():
    """Create the Flask app for use inside Celery tasks."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    return app


def make_celery(app):
    """
    Create and configure the Celery instance.
    Binds Flask app context to every Celery task so
    models and db.session work inside tasks.
    """
    celery_instance = Celery(
        app.import_name,
        broker=app.config['REDIS_URL'],
        backend=app.config['REDIS_URL'],
        include=[
            'tasks.reminders',  # tells Celery where to find tasks
            'tasks.reports'
        ]
    )

    celery_instance.conf.update(app.config)

    # Scheduled jobs
    celery_instance.conf.beat_schedule = {
        'daily-reminders': {
            'task': 'tasks.reminders.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        'monthly-report': {
            'task': 'tasks.reports.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=6, minute=0),
        },
    }

    celery_instance.conf.timezone = 'Asia/Kolkata'

    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask
    return celery_instance


# These two lines are critical — they must be at module level
# so that 'celery_app.celery' resolves correctly
flask_app = create_flask_app()
celery = make_celery(flask_app)