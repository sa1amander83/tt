
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tables(models.Model):
    TABLE_TYPES = (
        ('standard', 'Стандартный'),
        ('pro', 'Профессиональный')
    )

    number = models.PositiveIntegerField(unique=True, verbose_name="Номер стола")
    table_type = models.CharField(max_length=10, choices=TABLE_TYPES, default='standard', verbose_name="Тип стола")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"

    def __str__(self):
        return f"Стол #{self.number} ({self.get_table_type_display()})"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Пользователь")
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, related_name='bookings', verbose_name="Стол")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    equipment_rental = models.BooleanField(default=False, verbose_name="Аренда оборудования")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['start_time']

    def __str__(self):
        return f"Бронирование #{self.id} - Стол {self.table.number} ({self.start_time})"