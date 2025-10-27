import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

# Create Celery app
app = Celery('alx_travel_app')

# Load settings from Django settings.py file using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Optional: You can define periodic tasks (Celery Beat) here if needed later
# Example:
# app.conf.beat_schedule = {
#     'send-weekly-report': {
#         'task': 'listings.tasks.send_weekly_report',
#         'schedule': crontab(day_of_week='mon', hour=7, minute=0),
#     },
# }

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
