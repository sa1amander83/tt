import re
from datetime import timedelta
from django.utils.timezone import localtime

from bookings.models import TableTypePricing
from bookings.utils import get_applicable_pricing_plan


import re
from datetime import timedelta, date
from django.utils.timezone import localtime

from management.models import SpecialOffer
from management.LoyaltyEngine import LoyaltyEngine


class BookingEngine:
    def __init__(self, user, table, start_time, duration_minutes,
                 participants, equipment_items=None, is_group=False,
                 promo_code=None, manual_discount_percent=0):
        self.loyalty_level = None
        self.loyalty_discount_percent = None
        self.special_offer_discount_percent = None
        self.promo_code_discount_percent = None
        self.user = user
        self.table = table
        self.start_time = localtime(start_time)
        self.duration_minutes = duration_minutes
        self.participants = participants
        self.equipment_items = equipment_items or []
        self.is_group = is_group
        self.promo_code = promo_code
        self.manual_discount_percent = manual_discount_percent

        self.membership = self._get_membership()
        self.special_offer = self._get_special_offer()
        self.intervals = self._split_intervals()

        self.base_price = 0
        self.equipment_price = 0
        self.total_price = 0
        self.discount = 0
        self.pricing_plan = None
        self.pricing = None

        self.loyalty_engine = LoyaltyEngine(user)
    def _get_membership(self):
        # Активный и валидный абонемент
        membership = self.user.memberships.filter(is_active=True).first()
        if membership and membership.is_valid():
            return membership
        return None

    def _get_special_offer(self):
        offers = SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=self.start_time.date(),
            valid_to__gte=self.start_time.date()
        ).order_by('-discount_percent')

        current_day = str(self.start_time.isoweekday())
        current_time = self.start_time.time()

        for offer in offers:
            offer_days = re.findall(r'\d+', offer.weekdays)  # например "1,2,3"
            if current_day not in offer_days:
                continue
            if offer.time_from and offer.time_to:
                if not (offer.time_from <= current_time <= offer.time_to):
                    continue
            if not offer.apply_to_all and self.table not in offer.tables.all():
                continue
            return offer
        return None

    def _split_intervals(self):
        intervals = []
        current_time = self.start_time
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        while current_time < end_time:
            interval_end = min(current_time + timedelta(minutes=30), end_time)
            intervals.append((current_time, interval_end))
            current_time = interval_end
        return intervals

    def calculate_total_price(self):
        total_half_hours = len(self.intervals)
        full_hours = total_half_hours // 2
        leftover_half_hour = total_half_hours % 2

        plan = get_applicable_pricing_plan(self.start_time)
        self.pricing_plan = plan
        pricing = TableTypePricing.objects.filter(
            pricing_plan=plan,
            table_type=self.table.table_type
        ).first()

        if not pricing:
            self.total_price = 0
            return

        self.pricing = pricing

        # Ставки с учётом группы
        if self.is_group:
            hour_rate = pricing.hour_rate_group or 0
            half_hour_rate = pricing.half_hour_rate_group if pricing.half_hour_rate_group is not None else hour_rate / 2
        else:
            hour_rate = pricing.hour_rate or 0
            half_hour_rate = pricing.half_hour_rate if pricing.half_hour_rate is not None else hour_rate / 2

        total = full_hours * hour_rate + leftover_half_hour * half_hour_rate
        self.base_price = round(total)

        # 1. Спецпредложение
        if self.special_offer:
            total *= (100 - self.special_offer.discount_percent) / 100

        # 2. Абонемент
        if self.membership:
            mt = self.membership.membership_type
            if mt.includes_discount and mt.discount_percent > 0:
                total *= (100 - mt.discount_percent) / 100

        # 3. Промокод
        if self.promo_code:
            total *= (100 - self.promo_code.discount_percent) / 100

        # 4. Скидка по уровню лояльности
        loyalty_profile = getattr(self.user, 'loyaltyprofile', None)
        if loyalty_profile:
            loyalty_discount = self.loyalty_engine.profile.get_discount()
            if loyalty_discount > 0:
                total *= (100 - float(loyalty_discount)) / 100
            self.loyalty_discount_percent = float(loyalty_discount)
            self.loyalty_level = loyalty_profile.level
        else:
            self.loyalty_discount_percent = 0
            self.loyalty_level = None

        # 5. Ручная скидка
        if self.manual_discount_percent:
            total *= (100 - self.manual_discount_percent) / 100

        # Оборудование
        self.equipment_price = self._calculate_equipment_price()

        self.total_price = round(total + self.equipment_price)

    def _calculate_equipment_price(self):
        total = 0
        duration_half_hours = self.duration_minutes // 30
        for item in self.equipment_items:
            eq = item['equipment']
            qty = item.get('quantity', 1)
            rate = eq.price_per_half_hour
            total += rate * duration_half_hours * qty
        return round(total)
