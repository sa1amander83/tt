from django.db import models

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