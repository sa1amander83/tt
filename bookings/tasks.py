from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

from bookings.models import Booking


@shared_task
def cleanup_expired_pending_bookings():
    expiration_time = now() - timedelta(minutes=10)

    # Фильтруем просроченные бронирования со статусом "pending"
    expired_bookings = Booking.objects.filter(status='pending', created_at__lt=expiration_time)

    # Обновляем статус на "expired"
    count = expired_bookings.update(status='expired')

    return f"Marked {count} pending bookings as expired"