from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

from bookings.models import Booking


@shared_task
def cleanup_expired_pending_bookings():
    expiration_time = now() - timedelta(minutes=10)
    expired_bookings = Booking.objects.filter(status='pending', created_at__lt=expiration_time)
    count = expired_bookings.count()
    expired_bookings.delete()
    return f"Deleted {count} expired pending bookings"