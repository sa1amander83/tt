from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email


class UserManager(BaseUserManager):
    """ User manager """

    def _create_user(self, phone_number, password=None, **extra_fields):
        """Creates and returns a new user using a phone number"""
        if not phone_number:
            raise AttributeError("User must set a phone number")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.Role.USER)
        return self._create_user(phone_number, password, **extra_fields)

    def create_staffuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", User.Role.MANAGER)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model with roles """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        USER = 'USER', _('User')

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=15,
        unique=True,
        help_text="Ex: +1234567890",
    )
    email = models.EmailField(
        _("Email Address"),
        max_length=255,
        blank=True,
        null=True,
        validators=[validate_email],
        help_text="Ex: example@example.com",
    )
    first_name = models.CharField(
        _("First Name"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=150,
        blank=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        _("Role"),
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    is_staff = models.BooleanField(_("Staff status"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.phone_number} ({self.get_full_name()})"

    def get_full_name(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

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