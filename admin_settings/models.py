from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal

from django.db import models











class ClubSettings(models.Model):
    """Общие настройки клуба"""
    club_name = models.CharField(max_length=100, default="PingPong Club", verbose_name="Название клуба")
    club_email = models.EmailField(default="info@pingpongclub.com", verbose_name="Email клуба")
    club_phone = models.CharField(max_length=20, default="+7 (123) 456-78-90", verbose_name="Телефон клуба")
    club_address = models.TextField(default="г. Москва, ул. Спортивная, д. 123", verbose_name="Адрес клуба")
    club_description = models.TextField(blank=True, verbose_name="Описание клуба")
    currency = models.CharField(max_length=3, default="RUB", verbose_name="Валюта")
    timezone = models.CharField(max_length=50, default="Europe/Moscow", verbose_name="Часовой пояс")
    date_format = models.CharField(max_length=20, default="DD.MM.YYYY", verbose_name="Формат даты")
    time_format = models.CharField(max_length=10, default="24", verbose_name="Формат времени")

    # Настройки уведомлений
    notify_bookings = models.BooleanField(default=True, verbose_name="Уведомления о бронированиях")
    notify_cancellations = models.BooleanField(default=True, verbose_name="Уведомления об отменах")
    notify_payments = models.BooleanField(default=True, verbose_name="Уведомления о платежах")
    notify_registrations = models.BooleanField(default=True, verbose_name="Уведомления о регистрациях")

    # Настройки резервного копирования
    auto_backup = models.BooleanField(default=True, verbose_name="Автоматическое резервное копирование")
    backup_frequency = models.CharField(max_length=10, default="daily", verbose_name="Частота копирования")
    backup_time = models.TimeField(default="03:00", verbose_name="Время копирования")
    backup_retention = models.PositiveIntegerField(default=30, verbose_name="Хранить копий (дней)")

    class Meta:
        verbose_name = "Настройки клуба"
        verbose_name_plural = "Настройки клуба"

    def __str__(self):
        return "Настройки клуба"



class TableType(models.Model):
    """Типы столов с базовыми характеристиками"""
    name = models.CharField(max_length=50, verbose_name="Название типа")
    description = models.TextField(blank=True, verbose_name="Описание")
    max_capacity = models.PositiveIntegerField(default=2, verbose_name="Вместимость")


    class Meta:
        verbose_name = "Тип стола"
        verbose_name_plural = "Типы столов"

    def __str__(self):
        return self.name or f"Стол #{self.name}"


class Table(models.Model):
    """Модель стола"""
    number = models.PositiveIntegerField(unique=True, verbose_name="Номер стола")
    table_type = models.ForeignKey(TableType, on_delete=models.PROTECT, verbose_name="Тип стола")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    description = models.TextField(blank=True, verbose_name="Дополнительное описание")

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ['number']

    def __str__(self):
        return f"Стол #{self.number} ({self.table_type})"


class Equipment(models.Model):
    """Оборудование для аренды"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    price_per_half_hour = models.PositiveIntegerField(verbose_name="Цена за полчаса аренды", default=200)
    price_per_hour = models.PositiveIntegerField(verbose_name="Цена за час аренды", default=200)
    is_available = models.BooleanField(default=True, verbose_name="Доступно для аренды")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return self.name

class WorkingDay(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    )

    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK, unique=True)
    open_time = models.TimeField(default='09:00')
    close_time = models.TimeField(default='22:00')
    slot_duration = models.PositiveIntegerField(default=30)
    is_open = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Рабочий день"
        verbose_name_plural = "Рабочие дни"
        ordering = ['day']

    def __str__(self):
        return f"{self.get_day_display()}: {self.open_time} - {self.close_time}"

    @property
    def get_day_name(self):
        return dict(self.DAYS_OF_WEEK).get(self.day, '')

class Holiday(models.Model):
    HOLIDAY_STATUS = (
        ('closed', 'Закрыто'),
        ('shortened', 'Сокращенный день'),
        ('normal', 'Обычный режим'),
    )

    date = models.DateField(unique=True, verbose_name="Дата")
    description = models.CharField(max_length=200, verbose_name="Описание")
    status = models.CharField(max_length=10, choices=HOLIDAY_STATUS, default='closed', verbose_name="Статус")
    open_time = models.TimeField(blank=True, null=True, verbose_name="Время открытия")
    close_time = models.TimeField(blank=True, null=True, verbose_name="Время закрытия")

    class Meta:
        verbose_name = "Праздничный день"
        verbose_name_plural = "Праздничные дни"
        ordering = ['date']

    def __str__(self):
        return f"{self.date}: {self.description}"

    def clean(self):
        if self.status in ['shortened', 'normal'] and not (self.open_time and self.close_time):
            raise ValidationError("Для сокращенного/обычного режима нужно указать время работы")


from django.db import models

class AchievementCategory(models.TextChoices):
    ADULT = 'ADULT', 'Взрослые'
    CHILD = 'CHILD', 'Дети'
    UNIVERSAL = 'UNIVERSAL', 'Универсальные'

class Achievement(models.Model):
    user=models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Название ачивки")
    description = models.TextField(blank=True, help_text="Описание ачивки")
    category = models.CharField(max_length=20, choices=AchievementCategory.choices)
    icon = models.ImageField(upload_to='achievement_icons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    class Meta:
        verbose_name = "Ачивка"
        verbose_name_plural = "Ачивки"


class NotificationSettings(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='notification_settings')

    notify_bookings = models.BooleanField(default=True)
    notify_cancellations = models.BooleanField(default=True)
    notify_payments = models.BooleanField(default=True)
    notify_registrations = models.BooleanField(default=True)

    def __str__(self):
        return f"Настройки уведомлений для {self.user.user_name}"
