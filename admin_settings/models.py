from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal

from django.db import models

from bookings.models import Table



class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # запрещаем удаление

    @classmethod
    def load(cls):
        return cls.objects.first() or cls.objects.create()




# Create your models here.
# class Subscription(models.Model):
#     name = models.CharField(max_length=100, verbose_name="Название")
#     description = models.TextField(verbose_name="Описание")
#     price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
#     duration = models.PositiveIntegerField(verbose_name="Длительность (дней)")
#     is_active = models.BooleanField(default=True, verbose_name="Активен")
#     number_of_events = models.PositiveIntegerField(verbose_name='количество посещений', default=4)
#
#     class Meta:
#         verbose_name = "Абонемент"
#         verbose_name_plural = "Абонементы"
#
#     def __str__(self):
#         return self.name


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


class GeneralSettings(SingletonModel):
    site_title = models.CharField(max_length=200, verbose_name="Заголовок сайта")
    site_description = models.TextField(verbose_name="Описание сайта")
    contact_email = models.EmailField(verbose_name="Email для связи")
    contact_phone = models.CharField(max_length=20, verbose_name="Телефон для связи")

    class Meta:
        verbose_name = "Общие настройки"
        verbose_name_plural = "Общие настройки"

    def __str__(self):
        return "Общие настройки сайта"


class HomePageSettings(SingletonModel):
    header_title = models.CharField(max_length=200, verbose_name="Заголовок на главной")
    header_subtitle = models.CharField(max_length=300, verbose_name="Подзаголовок")
    about_text = models.TextField(verbose_name="О нас")
    mission_text = models.TextField(verbose_name="Миссия")

    class Meta:
        verbose_name = "Настройки главной страницы"
        verbose_name_plural = "Настройки главной страницы"

    def __str__(self):
        return "Настройки главной страницы"


class SocialLinks(SingletonModel):
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Социальные сети"
        verbose_name_plural = "Ссылки на социальные сети"

    def __str__(self):
        return "Социальные ссылки"


class SEOSettings(SingletonModel):
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.TextField(help_text="Через запятую")

    class Meta:
        verbose_name = "SEO-настройки"
        verbose_name_plural = "SEO-настройки"

    def __str__(self):
        return "SEO-настройки"


class FooterSettings(SingletonModel):
    footer_text = models.TextField(verbose_name="Текст в подвале")
    footer_links = models.JSONField(default=list, verbose_name="Ссылки в подвале")

    class Meta:
        verbose_name = "Настройки подвала"
        verbose_name_plural = "Настройки подвала"

    def __str__(self):
        return "Настройки подвала"


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


class BookingPackage(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
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