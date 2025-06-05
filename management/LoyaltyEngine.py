from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from management.models import LoyaltyProfile, LoyaltySettings, LevelBenefit


class LoyaltyEngine:
    def __init__(self, user):
        self.user = user
        self.profile = self._get_or_create_profile()
        self.settings = LoyaltySettings.load()

    def _get_or_create_profile(self):
        profile, created = LoyaltyProfile.objects.get_or_create(user=self.user)
        return profile

    def add_points_for_booking(self, booking_amount):
        """Начисление баллов за бронирование"""
        # Фиксированные баллы за бронирование
        self.profile.add_points(self.settings.points_per_booking)

        # Баллы за потраченную сумму
        points_from_amount = (booking_amount / self.settings.rubles_per_point) * self.settings.points_per_ruble
        self.profile.add_points(int(points_from_amount))

    def add_points_for_registration(self):
        """Начисление баллов за регистрацию"""
        self.profile.add_points(self.settings.points_for_registration)

    def add_points_for_review(self):
        """Начисление баллов за отзыв"""
        self.profile.add_points(self.settings.points_for_review)

    def redeem_points_for_discount(self, points):
        """Обмен баллов на скидку"""
        if not self.settings.enable_points_redemption:
            raise ValueError("Обмен баллов отключен")

        if points < self.settings.min_redemption:
            raise ValueError(f"Минимальное количество баллов для обмена: {self.settings.min_redemption}")

        if self.profile.points < points:
            raise ValueError("Недостаточно баллов")

        rubles = (points / self.settings.points_to_rubles) * self.settings.rubles_from_points
        self.profile.points -= points
        self.profile.save()
        return rubles

    def get_available_benefits(self):
        """Получение доступных привилегий"""
        return LevelBenefit.objects.filter(level=self.profile.level, is_active=True)

    def check_benefit(self, benefit_type):
        """Проверка наличия конкретной привилегии"""
        return LevelBenefit.objects.filter(
            level=self.profile.level,
            benefit_type=benefit_type,
            is_active=True
        ).exists()

    def apply_birthday_bonus(self):
        """Применение бонуса на день рождения"""
        if not self.profile.birthday_bonus_used:
            bonus = self.profile.get_birthday_bonus()
            self.profile.add_points(bonus)
            self.profile.birthday_bonus_used = True
            self.profile.save()
            return bonus
        return 0

    def apply_monthly_free_training(self):
        """Применение бесплатной тренировки"""
        if self.profile.has_monthly_free_training():
            self.profile.free_training_used = True
            self.profile.last_free_training_date = timezone.now().date()
            self.profile.save()
            return True
        return False

    def get_active_points(self):
        """Получение активных (не просроченных) баллов"""
        if not self.settings.enable_points_expiration:
            return self.profile.points

        expiration_date = timezone.now() - timedelta(days=30 * self.settings.points_expiration_months)
        if self.profile.joined_at > expiration_date:
            return self.profile.points
        return 0