from django.db import models
from django.utils import timezone
from decimal import Decimal




class Tables(models.Model):
    number = models.IntegerField(unique=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=300, verbose_name='Цена за час')
    price_per_half_hour = models.DecimalField(max_digits=6, decimal_places=2, default=200,
                                              verbose_name='Цена за пол часа')
    table_description = models.CharField(blank=True, null=True, max_length=12, verbose_name='Описание стола')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Стол {self.number}"

    class Meta:
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'


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
        BASIC = 'START', 'Старт'
        SILVER = 'SILVER', 'Серебряный'
        GOLD = 'GOLD', 'Золотой'
        PLATINUM = 'PLATINUM', 'Платиновый'

    LEVEL_THRESHOLDS = {
        Level.BASIC: 0,
        Level.SILVER: 1000,
        Level.GOLD: 5000,
        Level.PLATINUM: 10000,
    }

    LEVEL_DISCOUNTS = {
        Level.BASIC: Decimal('0.00'),
        Level.SILVER: Decimal('5.00'),    # 5% скидка
        Level.GOLD: Decimal('10.00'),     # 10% скидка
        Level.PLATINUM: Decimal('15.00'), # 15% скидка
    }


    points = models.PositiveIntegerField(default=0)
    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.BASIC,
    )
    joined_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)



    def get_discount(self):
        """Возвращает процент скидки по текущему уровню"""
        return self.LEVEL_DISCOUNTS.get(self.level, Decimal('0.00'))

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
