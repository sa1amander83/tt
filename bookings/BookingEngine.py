from datetime import timedelta
from django.utils.timezone import localtime

from admin_settings.models import Membership, SpecialOffer
from bookings.models import TableTypePricing
from bookings.utils import get_applicable_pricing_plan


class BookingEngine:
    def __init__(self, user, table, start_time, duration_minutes, participants, equipment_items=None, is_group=False):
        self.user = user
        self.table = table
        self.start_time = localtime(start_time)
        self.duration_minutes = duration_minutes
        self.participants = participants
        self.equipment_items = equipment_items or []
        self.is_group = is_group

        self.membership = self._get_membership()
        self.special_offer = self._get_special_offer()
        self.intervals = self._split_intervals()

        self.base_price = 0
        self.equipment_price = 0
        self.total_price = 0
        self.discount = 0
        self.pricing_plan = None
        self.pricing = None

    def _get_membership(self):
        return Membership.objects.filter(user=self.user, is_active=True).first()

    def _get_special_offer(self):
        return SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=self.start_time,
            valid_to__gte=self.start_time.date()
        ).order_by('-discount_percent').first()

    def _split_intervals(self):
        """Разбиваем бронь на 30-минутные интервалы"""
        intervals = []
        current_time = self.start_time
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)

        while current_time < end_time:
            interval_end = min(current_time + timedelta(minutes=30), end_time)
            intervals.append((current_time, interval_end))
            current_time = interval_end

        return intervals

    def calculate_total_price(self):
        total = 0
        pricing_used = set()

        for interval_start, interval_end in self.intervals:
            plan = get_applicable_pricing_plan(interval_start)
            self.pricing_plan = plan  # Последний применённый тариф
            pricing = TableTypePricing.objects.filter(
                pricing_plan=plan,
                table_type=self.table.table_type
            ).first()

            if not pricing:
                continue

            pricing_used.add(pricing)

            if self.is_group:
                rate = pricing.hour_rate_group
            else:
                rate = pricing.hour_rate

            # 30 минут = половина от часовой ставки
            interval_price = rate / 2
            total += interval_price

        self.pricing = max(pricing_used, key=lambda p: p.min_duration, default=None)
        self.base_price = round(total)

        # Применение скидки от спецпредложения
        if self.special_offer:
            self.discount = self.special_offer.discount_percent
            total *= (100 - self.discount) / 100

        # Применение абонемента (например, бесплатные часы)
        if self.membership:
            total *= 0.8  # Пример: 20% скидка по абонементу, адаптируй под свою логику

        self.total_price = round(total)

        # Расчёт оборудования
        self.equipment_price = self._calculate_equipment_price()
        self.total_price += self.equipment_price

    def _calculate_equipment_price(self):
        total = 0
        duration_half_hours = self.duration_minutes // 30

        for item in self.equipment_items:
            eq = item['equipment']
            qty = item.get('quantity', 1)
            rate = eq.price_per_half_hour
            total += rate * duration_half_hours * qty

        return round(total)
