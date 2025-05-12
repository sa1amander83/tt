from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model




class TableType(models.Model):
    """Типы столов с базовыми характеристиками"""
    name = models.CharField(max_length=50, verbose_name="Название типа")
    description = models.TextField(blank=True, verbose_name="Описание")
    default_capacity = models.PositiveIntegerField(default=2, verbose_name="Вместимость по умолчанию")


    class Meta:
        verbose_name = "Тип стола"
        verbose_name_plural = "Типы столов"

    def __str__(self):
        return self.name


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


class PricingPlan(models.Model):
    """Модель тарифного плана"""
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    description = models.TextField(blank=True, verbose_name="Описание тарифа")
    is_default = models.BooleanField(default=False, verbose_name="Тариф по умолчанию")
    valid_from = models.DateField(verbose_name="Действует с")
    valid_to = models.DateField(blank=True, null=True, verbose_name="Действует до")

    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"

    def __str__(self):
        return self.name


class TableTypePricing(models.Model):
    """Цены для типов столов в разных тарифных планах"""
    table_type = models.ForeignKey(TableType, on_delete=models.CASCADE, verbose_name="Тип стола")
    pricing_plan = models.ForeignKey(PricingPlan, on_delete=models.CASCADE, verbose_name="Тарифный план")
    hour_rate = models.PositiveIntegerField(verbose_name="Цена за час (стандарт)",default=400)
    hour_rate_group = models.PositiveIntegerField(verbose_name="Цена за час (группа)")
    min_duration = models.PositiveIntegerField(default=1, verbose_name="Минимальная длительность (часы)")
    max_duration = models.PositiveIntegerField(default=3, verbose_name="Максимальная длительность (часы)")

    class Meta:
        verbose_name = "Цена типа стола"
        verbose_name_plural = "Цены типов столов"
        unique_together = ('table_type', 'pricing_plan')


    def __str__(self):
        return f"{self.table_type} - {self.pricing_plan}"


class Equipment(models.Model):
    """Оборудование для аренды"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    price_per_hour = models.PositiveIntegerField(verbose_name="Цена за час аренды", default=200)
    is_available = models.BooleanField(default=True, verbose_name="Доступно для аренды")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """Модель временных слотов столов"""
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Стол")
    pricing_plan = models.ForeignKey(PricingPlan, on_delete=models.PROTECT, verbose_name="Тарифный план")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    is_available = models.BooleanField(default=True, verbose_name="Доступен для брони")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован (тех. работы)")

    class Meta:
        verbose_name = "Временной слот"
        verbose_name_plural = "Временные слоты"
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['table', 'start_time', 'end_time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['table', 'start_time', 'end_time'],
                name='unique_table_timeslot'
            )
        ]

    def __str__(self):
        return f"{self.table} {self.start_time.strftime('%d.%m.%Y %H:%M')}-{self.end_time.strftime('%H:%M')}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Время окончания должно быть позже времени начала")

        # Проверка на пересечение с другими слотами
        overlapping = TimeSlot.objects.filter(
            table=self.table,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk).exists()

        if overlapping:
            raise ValidationError("Слот пересекается с существующим бронированием")

    @property
    def duration_hours(self):
        """Длительность слота в часах"""
        return (self.end_time - self.start_time).total_seconds() / 3600

User='accounts.User'
class Booking(models.Model):
    """Модель бронирования"""
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Пользователь")
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name='bookings',
                                 verbose_name="Временной слот")
    pricing_plan = models.ForeignKey(PricingPlan, on_delete=models.PROTECT, verbose_name="Тарифный план")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    # Информация о бронировании
    participants = models.PositiveIntegerField(default=2, verbose_name="Количество участников")
    is_group = models.BooleanField(default=False, verbose_name="Групповое бронирование")
    equipment = models.ManyToManyField(Equipment, through='BookingEquipment', blank=True, verbose_name="Оборудование")

    # Цены и стоимость
    base_price = models.PositiveIntegerField(verbose_name="Базовая стоимость", default=400)
    equipment_price = models.PositiveIntegerField(default=0, verbose_name="Стоимость оборудования")
    total_price = models.PositiveIntegerField(verbose_name="Итоговая стоимость")

    # Дополнительная информация
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронирование #{self.id} - {self.user} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Автоматическое заполнение полей при создании
        if not self.pk:
            self.start_time = self.timeslot.start_time
            self.end_time = self.timeslot.end_time
            self.table = self.timeslot.table
            self.pricing_plan = self.timeslot.pricing_plan

            # Расчет стоимости
            self.calculate_prices()

        super().save(*args, **kwargs)

    def calculate_prices(self):
        """Расчет стоимости бронирования"""
        pricing = TableTypePricing.objects.get(
            table_type=self.timeslot.table.table_type,
            pricing_plan=self.timeslot.pricing_plan
        )

        duration = self.timeslot.duration_hours

        # Базовая стоимость
        if self.is_group:
            self.base_price = pricing.hour_rate_group * duration
        else:
            self.base_price = pricing.hour_rate * duration

        # Стоимость оборудования
        equipment_price = sum(
            eq.price_per_hour * duration
            for eq in self.equipment.all()
        )
        self.equipment_price = equipment_price

        # Итоговая стоимость
        self.total_price = self.base_price + self.equipment_price


class BookingEquipment(models.Model):
    """Промежуточная модель для оборудования в бронировании"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Оборудование в бронировании"
        verbose_name_plural = "Оборудование в бронированиях"


    def __str__(self):
        return f"{self.equipment} x{self.quantity} в брони #{self.booking.id}"