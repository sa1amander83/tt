from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

from bookings.models import Booking


@shared_task
def cleanup_expired_pending_bookings():
    expiration_time = now() - timedelta(minutes=10)

    # 1. Просроченные бронирования в статусе 'pending' (ожидание оплаты более 10 минут)
    pending_expiration_time = expiration_time - timedelta(minutes=10)
    expired_pending_bookings = Booking.objects.filter(status='pending', created_at__lt=pending_expiration_time)
    expired_count = expired_pending_bookings.update(status='expired')

    # 2. Завершённые по времени бронирования со статусом 'paid'
    completed_bookings = Booking.objects.filter(
        status='paid',
        end_time__lt=expiration_time  # Предположим, у тебя есть поле end_time или аналогичное
    )
    completed_count = completed_bookings.update(status='completed')

    return f"Marked {expired_count} pending bookings as expired, {completed_count} paid bookings as completed"