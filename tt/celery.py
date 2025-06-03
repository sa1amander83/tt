from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
# Устанавливаем переменную окружения ДО создания объекта Celery!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tt.settings')

app = Celery('tt')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Для Flower и мониторинга
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True

# Автоматически находит tasks.py в приложениях, указанных в INSTALLED_APPS
# app.autodiscover_tasks()
app.autodiscover_tasks(['bookings'])

app.conf.beat_schedule = {
    'cleanup-expired-pending-bookings-every-minute': {
        'task': 'bookings.tasks.cleanup_expired_pending_bookings',
        'schedule': 600.0,  # запускать каждые 10 минут
    },
}

# (Опционально) если хочешь добавить логирование, например:
if __name__ == '__main__':
    app.start()
