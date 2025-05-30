from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from accounts.models import User
from yookassa import  Payment
import logging

from admin_settings.models import Table
from bookings.models import Booking

logger = logging.getLogger(__name__)


class EventManager(models.Manager):
    """ Event manager """

    def get_all_events(self, user):
        events = Booking.objects.filter(user=user, is_active=True, is_deleted=False)
        return events

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'table')

    def for_user(self, user):
        return self.get_queryset().filter(user=user)


    def get_running_events(self, user):
        running_events = Booking.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            end_time__gte=datetime.now(),
            start_time__lte=datetime.now()
        ).order_by("start_time")
        return running_events

    def get_completed_events(self, user):
        completed_events = Booking.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            end_time__lt=datetime.now().date(),
        )
        return completed_events

    def get_upcoming_events(self, user):
        upcoming_events = Booking.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            start_time__gt=datetime.now(),
            end_time__gt=datetime.now(),
        )
        return upcoming_events

    def available_slots(self, table, date):
        start = datetime.combine(date, datetime.min.time())
        end = start + timedelta(days=1)
        # return TimeSlot.objects.filter(
        #     table=table,
        #     start_time__range=(start, end),
        #     is_available=True
        # )
class EventAbstract(models.Model):
    """ Event abstract model """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



# class Event(EventAbstract):
#     """ Event model """
#     PAYMENT_STATUSES = (
#         ('pending', 'Ожидает оплаты'),
#         ('paid', 'Оплачено'),
#         ('canceled', 'Отменено'),
#         ('failed', 'Ошибка оплаты'),
#     )
#
#     constraints = [
#         models.UniqueConstraint(
#             fields=['user', 'start_time', 'end_time', 'table'],
#             name='unique_booking_for_user'
#         )
#     ]
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", verbose_name='гость')
#
#     start_time = models.DateTimeField(verbose_name='Время начала брони')
#     end_time = models.DateTimeField(verbose_name='Время окончания брони')
#     total_cost = models.FloatField(default=300)
#
#     # Платежная информация
#     payment_id = models.CharField(max_length=100, blank=True)
#     payment_status = models.CharField(
#         max_length=20,
#         choices=PAYMENT_STATUSES,
#         default='pending'
#     )
#
#     equipment_rental = models.BooleanField(default=False, verbose_name="Аренда оборудования")
#
#     payment_data = models.JSONField(default=dict, blank=True)
#     timeslot = models.ForeignKey("TimeSlot", on_delete=models.PROTECT)
#     participants = models.PositiveIntegerField(default=1)
#     notes = models.TextField(blank=True)
#     is_canceled = models.BooleanField('Отменено', default=False)
#     cancel_reason = models.TextField('Причина отмены', blank=True, null=True)
#     table = models.ForeignKey(Tables, on_delete=models.CASCADE, related_name="events", null=True, default=1,
#                               verbose_name='Стол')
#     total_time = models.FloatField(default=0)
#     is_paid = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
#     objects = EventManager()
#     def __str__(self):
#         return f"{self.start_time} - {self.end_time} - {self.table.number} - {self.user}" if self.user else self.user
#
#     def get_absolute_url(self):
#         return reverse("bookings:booking-detail", kwargs={"pk": self.id})
#
#
#     def clean(self):
#         if self.start_time >= self.end_time:
#             raise ValidationError("Некорректное время бронирования")
#
#
#     def save(self, *args, **kwargs):
#         self.full_clean()
#         self.total_cost = self.calculate_cost()
#         super().save(*args, **kwargs)
#
#
#     def calculate_cost(self):
#         duration = (self.end_time - self.start_time).total_seconds() / 3600
#         return round(duration * self.table.hourly_rate, 2)
#
#
#     # def update_payment_status(self):
#     #     try:
#     #         payment = Payment.find_one(self.payment_id)
#     #         self.payment_status = payment.status
#     #         self.payment_data = dict(payment)
#     #         self.save()
#     #         return True
#     #     except Exception as e:
#     #         logger.error(f"Payment status update failed: {str(e)}")
#     #         return False
#
#
#     @property
#     def duration(self):
#         return self.end_time - self.start_time
#
#
#     def cancel_booking(self, reason=None):
#         self.payment_status = 'canceled'
#         self.cancel_reason = reason
#         self.timeslot.is_available = True
#         self.timeslot.save()
#         self.save()
#
#     def update_payment_status(self):
#         """Обновляет статус платежа из ЮKassa"""
#         if not self.payment_id:
#             return False
#
#         try:
#             payment = Payment.find_one(self.payment_id)
#             self.payment_status = payment.status
#             self.is_paid = (payment.status == 'succeeded')
#             self.save()
#             return True
#         except Exception as e:
#             logger.error(f"Error updating payment status: {str(e)}")
#             return False



class UserEventStats(EventAbstract):
    """ User event stats """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_stats")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="event_stats")
    total_time = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    total_events = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)




# models.py
# class EventMember(EventAbstract):
#     """ Event member model """
#
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="events")
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="event_members"
#     )
#
#     class Meta:
#         unique_together = ["event", "user"]

    # def __str__(self):
    #     return str(self.user)


