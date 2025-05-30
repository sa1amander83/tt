
from datetime import datetime
from django.db import models




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
    from admin_settings.models import TableType
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

