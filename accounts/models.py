import os

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email, MinValueValidator, MaxValueValidator

from admin_settings.models import LoyaltyProfile



def user_photo_upload_path(instance, filename):
    # instance - объект User
    # filename - исходное имя файла
    phone = instance.phone or "unknown_phone"
    # Можно очистить номер телефона от символов, если нужно:
    phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
    return os.path.join('user_photos', phone_clean, filename)





class UserManager(BaseUserManager):
    """ User manager """

    def _create_user(self, phone, password=None, **extra_fields):
        """Creates and returns a new user using a phone number"""
        if not phone:
            raise AttributeError("User must set a phone number")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.Role.USER)
        return self._create_user(phone, password, **extra_fields)

    def create_staffuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.Role.MANAGER)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        return self._create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model with roles """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        USER = 'USER', _('User')

    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Начинающий'
        INTERMEDIATE = 'intermediate', 'Средний'
        ADVANCED = 'advanced', 'Продвинутый'
        PROFESSIONAL = 'professional', 'Профессиональный'

    phone = models.CharField(
        _("Phone Number"),
        max_length=15,
        unique=True,
        help_text="Ex: +1234567890",
    )
    email = models.EmailField(
        _("Email Address"),
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_email],
        help_text="Ex: example@example.com",
    )
    user_name = models.CharField(
        _("user name"),
        max_length=150,
        blank=True,
    )


    role = models.CharField(
        _("Role"),
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    level = models.CharField(
        _("Уровень"),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
        help_text="Уровень пользователя"
    )
    status=models.CharField(_("Статус"), max_length=10, choices=[('active', 'Активен'),
                                                                ('not_active', 'Не активен'), ('blocked', 'Заблокирован')], default='active')
    user_age=models.PositiveIntegerField(_("Возраст"), blank=True, null=True ,    validators=[
        MinValueValidator(5, message="Возраст должен быть не меньше 5 лет"),
        MaxValueValidator(99, message="Возраст должен быть не больше 99 лет"),
    ])
    is_staff = models.BooleanField(_("Статус"), default=False)
    date_joined = models.DateTimeField(_("Зарегистрирован"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Был в последний раз"), auto_now=True)
    loyalty=models.ForeignKey(LoyaltyProfile, on_delete=models.SET_NULL, blank=True, null=True)
    photo = models.ImageField(
        upload_to=user_photo_upload_path,
        blank=True,
        null=True,
        verbose_name='Фотография пользователя'
    )
    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["user_name", "email"]

    def __str__(self):
        return f"{self.phone} ({self.user_name})"



    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    def save(self, *args, **kwargs):
        # Автоматически назначаем is_staff=True для админов и менеджеров
        if self.role in [self.Role.ADMIN, self.Role.MANAGER]:
            self.is_staff = True
        super().save(*args, **kwargs)


