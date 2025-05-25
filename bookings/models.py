from datetime import datetime

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
    time_from = models.TimeField(null=True, blank=True, verbose_name="Начало действия")
    time_to = models.TimeField(null=True, blank=True, verbose_name="Окончание действия")
    weekdays = models.CharField(max_length=13, default="1234567", verbose_name="Дни недели")  # '1' = Пн ... '7' = Вс

    def is_applicable(self, dt:     datetime) -> bool:
        """Проверка, применим ли тариф в конкретное время"""
        if str(dt.isoweekday()) not in self.weekdays:
            return False
        if self.time_from and self.time_to:
            return self.time_from <= dt.time() < self.time_to
        return True

        
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
    half_hour_rate = models.PositiveIntegerField(verbose_name="Цена за полчаса (стандарт)",default=250)
    hour_rate_group = models.PositiveIntegerField(verbose_name="Цена за час (группа)")
    min_duration = models.PositiveIntegerField(default=30, verbose_name="Минимальная длительность (минуты)")
    max_duration = models.PositiveIntegerField(default=180, verbose_name="Максимальная длительность (минуты)")

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
    price_per_half_hour = models.PositiveIntegerField(verbose_name="Цена за полчаса аренды", default=200)
    price_per_hour = models.PositiveIntegerField(verbose_name="Цена за час аренды", default=200)
    is_available = models.BooleanField(default=True, verbose_name="Доступно для аренды")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return self.name


    @property
    def quantity_range(self):
        return range(1, self.quantity_available + 1)




User='accounts.User'
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Пользователь")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Стол")
    pricing = models.ForeignKey(TableTypePricing, on_delete=models.PROTECT, verbose_name="Ценообразование")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    participants = models.PositiveIntegerField(default=2, verbose_name="Количество участников")
    is_group = models.BooleanField(default=False, verbose_name="Групповое бронирование")
    equipment = models.ManyToManyField(Equipment, through='BookingEquipment', blank=True, verbose_name="Оборудование")

    base_price = models.PositiveIntegerField(verbose_name="Базовая стоимость", default=400)
    equipment_price = models.PositiveIntegerField(default=0, verbose_name="Стоимость оборудования")
    total_price = models.PositiveIntegerField(verbose_name="Итоговая стоимость")

    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронирование #{self.id} - {self.user} ({self.get_status_display()})"

    def calculate_prices(self):
        pricing = self.pricing
        duration = (self.end_time - self.start_time).total_seconds() / 3600

        if self.is_group:
            self.base_price = pricing.hour_rate_group * duration
        else:
            self.base_price = pricing.hour_rate * duration

        # Получаем связанные BookingEquipment записи
        booking_equipments = self.bookingequipment_set.all()

        equipment_price = 0
        for be in booking_equipments:
            equipment_price += be.equipment.price_per_hour * duration * be.quantity

        self.equipment_price = int(equipment_price)
        self.total_price = int(self.base_price + self.equipment_price)

    def save(self, *args, **kwargs):
        # Сначала сохраняем объект, если он новый
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Если объект уже сохранён и есть id, тогда можно вычислять цены
        if not is_new:
            self.calculate_prices()
            # Чтобы не попасть в бесконечный цикл, при пересчёте цен можно сделать update напрямую:
            Booking.objects.filter(pk=self.pk).update(
                base_price=self.base_price,
                equipment_price=self.equipment_price,
                total_price=self.total_price,
            )


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