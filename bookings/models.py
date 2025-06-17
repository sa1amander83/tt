from datetime import datetime
from decimal import Decimal

from django.db import models
from django.utils import timezone

from management.models import PromoCode, SpecialOffer
# from admin_settings.models import Table, Equipment
from pricing.models import TableTypePricing

User='accounts.User'



class BookingPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    total_minutes = models.PositiveIntegerField()
    used_minutes = models.PositiveIntegerField(default=0)
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def remaining_minutes(self):
        return max(self.total_minutes - self.used_minutes, 0)

    def is_valid(self):
        return self.is_active and self.valid_until >= timezone.now().date()

    def consume(self, minutes):
        if self.remaining_minutes() >= minutes:
            self.used_minutes += minutes
            self.save()
            return True
        return False


class Booking(models.Model):
    from admin_settings.models import Table, Equipment
    STATUS_CHOICES = (
    ('processing', 'Идет сейчас'),
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
        ('expired', 'Просрочено'),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Пользователь"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        verbose_name="Стол"
    )
    pricing = models.ForeignKey(
        TableTypePricing,
        on_delete=models.PROTECT,
        verbose_name="Ценообразование"
    )
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус",

    )

    promo_code = models.ForeignKey(
        'management.PromoCode',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Промокод",
        help_text="Применённый промокод, если был"
    )
    promo_code_discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name="Скидка по промокоду (%)"
    )

    special_offer = models.ForeignKey(
     'management.SpecialOffer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Специальное предложение",
        help_text="Применённое спецпредложение, если было"
    )
    special_offer_discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name="Скидка по спецпредложению (%)"
    )

    participants = models.PositiveIntegerField(
        default=2,
        verbose_name="Количество участников"
    )
    is_group = models.BooleanField(
        default=False,
        verbose_name="Групповое бронирование"
    )
    equipment = models.ManyToManyField(
        Equipment,
        through='BookingEquipment',
        blank=True,
        verbose_name="Оборудование"
    )

    base_price = models.PositiveIntegerField(
        verbose_name="Базовая стоимость",
        default=400
    )
    equipment_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Стоимость оборудования"
    )
    total_price = models.PositiveIntegerField(verbose_name="Итоговая стоимость")
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    class LoyaltyLevel(models.TextChoices):
        BASIC = 'BASIC', 'Старт'
        SILVER = 'SILVER', 'Серебряный'
        GOLD = 'GOLD', 'Золотой'
        PLATINUM = 'PLATINUM', 'Платиновый'

    loyalty_level = models.CharField(
        max_length=10,
        choices=LoyaltyLevel.choices,
        null=True,
        blank=True,
    )
    loyalty_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    expires_at = models.DateTimeField(default=datetime.now() + timezone.timedelta(days=1), verbose_name="Срок действия")
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронирование #{self.id} - {self.user} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not is_new:
            self.calculate_prices()
            # Обновляем цены напрямую, чтобы избежать бесконечной рекурсии
            Booking.objects.filter(pk=self.pk).update(
                base_price=self.base_price,
                equipment_price=self.equipment_price,
                total_price=self.total_price,
            )

    def calculate_prices(self):
        from bookings.BookingEngine import BookingEngine

        equipment_data = [
            {'equipment': be.equipment, 'quantity': be.quantity}
            for be in self.bookingequipment_set.all()
        ]

        engine = BookingEngine(
            user=self.user,
            table=self.table,
            start_time=self.start_time,
            duration_minutes=int((self.end_time - self.start_time).total_seconds() / 60),
            participants=self.participants,
            equipment_items=equipment_data,
            is_group=self.is_group,
            promo_code=self.promo_code,
        )

        engine.calculate_total_price()

        self.base_price = engine.base_price
        self.equipment_price = engine.equipment_price
        self.total_price = engine.total_price

        self.promo_code_discount_percent = engine.promo_code_discount_percent or 0
        self.special_offer_discount_percent = engine.special_offer_discount_percent or 0

class BookingEquipment(models.Model):
    from admin_settings.models import  Equipment
    """Промежуточная модель для оборудования в бронировании"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Оборудование в бронировании"
        verbose_name_plural = "Оборудование в бронированиях"


    def __str__(self):
        return f"{self.equipment} x{self.quantity} в брони #{self.booking.id}"

