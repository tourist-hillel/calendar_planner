import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_planner.settings')

app = Celery('calendar_planner')
app.config_from_object('django.conf:settings', namespace='CELECRY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
