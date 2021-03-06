import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checker_bot.settings')

import django

django.setup()

app = Celery('checker_bot', include=['checker_bot.tasks'])
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'start_task_check_bot': {
        'task': 'checker_bot.tasks.start_task_check_bot',
        'schedule': crontab(minute='*/1')
    },
    'active_ban_session': {
        'task': 'checker_bot.tasks.active_ban_session',
        'schedule': crontab(minute='*/5')
    },
    'add_client': {
        'task': 'checker_bot.tasks.add_client',
        'schedule': crontab(minute='*/5')
    }
}
