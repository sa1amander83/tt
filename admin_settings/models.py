from django.db import models
from django.utils import timezone
from decimal import Decimal






# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    duration = models.PositiveIntegerField(verbose_name="Длительность (дней)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    number_of_events = models.PositiveIntegerField(verbose_name='количество посещений', default=4)

    class Meta:
        verbose_name = "Абонемент"
        verbose_name_plural = "Абонементы"

    def __str__(self):
        return self.name


from django.db import models




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
