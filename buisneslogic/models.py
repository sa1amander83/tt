from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from admin_settings.models import Table


class LoyaltyProfile(models.Model):
    class Level(models.TextChoices):
        BASIC = 'BASIC', 'Старт'
        SILVER = 'SILVER', 'Серебряный'
        GOLD = 'GOLD', 'Золотой'
        PLATINUM = 'PLATINUM', 'Платиновый'

    # Пороги баллов для уровней
    LEVEL_THRESHOLDS = {
        Level.BASIC: 0,
        Level.SILVER: 1000,
        Level.GOLD: 5000,
        Level.PLATINUM: 10000,
    }

    # Скидки по уровням
    LEVEL_DISCOUNTS = {
        Level.BASIC: Decimal('0.00'),
        Level.SILVER: Decimal('5.00'),
        Level.GOLD: Decimal('10.00'),
        Level.PLATINUM: Decimal('20.00'),
    }

    # Дни раннего бронирования
    LEVEL_EARLY_BOOKING = {
        Level.BASIC: 8,
        Level.SILVER: 14,
        Level.GOLD: 14,
        Level.PLATINUM: 30,
    }

    # Часы для бесплатной отмены
    LEVEL_CANCELLATION_TIME = {
        Level.BASIC: 2,
        Level.SILVER: 2,
        Level.GOLD: 2,
        Level.PLATINUM: 1,
    }

    # Бонусы на день рождения
    LEVEL_BIRTHDAY_BONUS = {
        Level.BASIC: 500,
        Level.SILVER: 500,
        Level.GOLD: 500,
        Level.PLATINUM: 1000,
    }

    points = models.PositiveIntegerField(default=0)
    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.BASIC,
    )
    joined_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    birthday_bonus_used = models.BooleanField(default=False)
    free_training_used = models.BooleanField(default=False)
    last_free_training_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Профиль лояльности'
        verbose_name_plural = 'Профили лояльности'

    def __str__(self):
        return f'{self.get_level_display()} (баллы: {self.points})'

    def get_discount(self):
        """Возвращает процент скидки по текущему уровню"""
        return self.LEVEL_DISCOUNTS.get(self.level, Decimal('0.00'))

    def get_early_booking_days(self):
        """Возвращает количество дней раннего бронирования"""
        return self.LEVEL_EARLY_BOOKING.get(self.level, 0)

    def get_cancellation_time(self):
        """Возвращает часы для бесплатной отмены"""
        return self.LEVEL_CANCELLATION_TIME.get(self.level, 2)

    def get_birthday_bonus(self):
        """Возвращает количество бонусных баллов на ДР"""
        return self.LEVEL_BIRTHDAY_BONUS.get(self.level, 0)

    def has_priority_support(self):
        """Есть ли приоритетная поддержка"""
        return self.level == self.Level.PLATINUM

    def has_monthly_free_training(self):
        """Доступна ли бесплатная тренировка"""
        if self.level == self.Level.PLATINUM and not self.free_training_used:
            # Проверяем, если прошло больше месяца с последней тренировки
            if not self.last_free_training_date or \
               (timezone.now().date() - self.last_free_training_date).days >= 30:
                return True
        return False

    def add_points(self, amount):
        """Начисляет баллы и пересчитывает уровень"""
        self.points += amount
        self.update_level()
        self.save()

    def update_level(self):
        """Обновляет уровень в зависимости от количества баллов"""
        for level, threshold in sorted(self.LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if self.points >= threshold:
                if self.level != level:
                    self.level = level
                break

    def use_birthday_bonus(self):
        """Использовать бонус на день рождения"""
        if not self.birthday_bonus_used:
            self.add_points(self.get_birthday_bonus())
            self.birthday_bonus_used = True
            self.save()
            return True
        return False

    def use_free_training(self):
        """Использовать бесплатную тренировку"""
        if self.has_monthly_free_training():
            self.free_training_used = True
            self.last_free_training_date = timezone.now().date()
            self.save()
            return True
        return False

    def reset_monthly_benefits(self):
        """Сброс ежемесячных бонусов (вызывать в начале месяца)"""
        self.free_training_used = False
        self.save()

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def is_valid(self):
        today = date.today()
        return self.is_active and self.valid_from <= today <= self.valid_to

    def is_valid_for_user(self, user):
        if not self.is_valid():
            return False
        if self.user and self.user != user:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def apply_code(self):
        if self.usage_limit is not None:
            self.used_count = models.F('used_count') + 1
            self.save(update_fields=['used_count'])

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

# Create your models here.

class MembershipType(models.Model):
    """Типы абонементов"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    duration_days = models.PositiveIntegerField(default=30, verbose_name="Длительность (дней)")
    price = models.PositiveIntegerField(verbose_name="Стоимость")
    discount_percent = models.PositiveIntegerField(default=0)
    included_hours = models.PositiveIntegerField(default=0)  # 0 = не ограничено

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    includes_booking = models.BooleanField(default=True, verbose_name="Включает бронирование")
    includes_discount = models.BooleanField(default=False, verbose_name="Включает скидки")
    includes_tournaments = models.BooleanField(default=False, verbose_name="Включает турниры")
    includes_training = models.BooleanField(default=False, verbose_name="Включает тренировки")
    is_group_plan = models.BooleanField(default=False)
    is_unlimited = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Тип абонемента"
        verbose_name_plural = "Типы абонементов"

    def __str__(self):
        return self.name

class Membership(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='memberships')
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE, verbose_name="Тип абонемента")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    used_minutes = models.PositiveIntegerField(default=0)  # сколько уже потрачено

    class Meta:
        verbose_name = "Абонемент"
        verbose_name_plural = "Абонементы"

    def __str__(self):
        return f"{self.user} - {self.membership_type.name}"

    def is_valid(self):
        today = date.today()
        return self.is_active and self.start_date <= today <= self.end_date

class SpecialOffer(models.Model):
    """Специальные предложения и скидки"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    discount_percent = models.PositiveIntegerField(verbose_name="Скидка (%)")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    valid_from = models.DateField(verbose_name="Действует с")
    valid_to = models.DateField(verbose_name="Действует до")
    apply_to_all = models.BooleanField(default=False, verbose_name="Применять ко всем столам")
    tables = models.ManyToManyField(Table, blank=True, verbose_name="Применять к столам")
    time_from = models.TimeField(blank=True, null=True, verbose_name="Время начала")
    time_to = models.TimeField(blank=True, null=True, verbose_name="Время окончания")
    weekdays = models.CharField(max_length=50, blank=True, default="1,2,3,4,5,6,7",
                                verbose_name="Дни недели (1-Пн,7-Вс)")

    class Meta:
        verbose_name = "Специальное предложение"
        verbose_name_plural = "Специальные предложения"

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"
    def get_weekdays_display(self):
        days_map = {
            '1': 'Пн',
            '2': 'Вт',
            '3': 'Ср',
            '4': 'Чт',
            '5': 'Пт',
            '6': 'Сб',
            '7': 'Вс'
        }
        days = self.weekdays.split(',')
        return ', '.join(days_map.get(day, '') for day in days if day in days_map)
    def get_tables_display(self):
        return ', '.join(table.table_type.name for table in self.tables.all())