from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Q
from django.utils.timezone import make_aware, now

from admin_settings.models import Membership, LoyaltyProfile, SpecialOffer
from bookings.models import Booking, BookingEquipment, TableTypePricing, PricingPlan, Equipment

from django.db.models import Q

class BookingEngine:
    def __init__(self, user, table, start_time: datetime, duration_minutes: int, participants=2, equipment_items=None):
        """
        equipment_items — список словарей: [{"equipment": Equipment instance, "quantity": int}]
        """
        self.user = user
        self.table = table
        self.start_time = make_aware(start_time) if start_time.tzinfo is None else start_time
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.duration_minutes = duration_minutes
        self.participants = participants
        self.is_group = participants > table.table_type.default_capacity

        # Оптимизация: если переданы id оборудования, загружаем модели
        if equipment_items and equipment_items and isinstance(equipment_items[0], dict):
            eq_ids = [item['equipment'].id if hasattr(item['equipment'], 'id') else item['equipment'] for item in equipment_items]
            equipment_map = {eq.id: eq for eq in Equipment.objects.filter(id__in=eq_ids).only('id', 'price_per_hour', 'price_per_half_hour')}
            self.equipment_items = []
            for item in equipment_items:
                eq_obj = item['equipment'] if hasattr(item['equipment'], 'id') else equipment_map.get(item['equipment'])
                if eq_obj:
                    self.equipment_items.append({
                        'equipment': eq_obj,
                        'quantity': item.get('quantity', 1)
                    })
        else:
            self.equipment_items = equipment_items or []

        self.membership = self.get_active_membership()
        self.loyalty = self.get_loyalty_profile()
        self.special_offer = self.get_applicable_special_offer()
        self.pricing_plan = self.get_pricing_plan()
        self.pricing = self.get_pricing()
        self.base_price = 0
        self.equipment_price = 0
        self.total_price = 0

    # ---------------- Availability ----------------
    def is_table_available(self):
        # Проверяем, что у выбранного стола нет пересечений по времени бронирования
        overlapping_bookings = Booking.objects.filter(
            table=self.table,
            status__in=['confirmed', 'pending'],  # возможно другие статус, которые блокируют
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists()
        return not overlapping_bookings



    # ---------------- Membership ----------------
    def get_active_membership(self):
        return Membership.objects.filter(
            user=self.user,
            is_active=True,
            start_date__lte=now().date(),
            end_date__gte=now().date()
        ).first()

    def has_unlimited_membership(self):
        return self.membership and self.membership.membership_type.is_unlimited

    def has_remaining_minutes(self):
        if not self.membership or self.has_unlimited_membership():
            return False
        used = self.membership.used_minutes
        allowed = self.membership.membership_type.included_hours * 60
        return (allowed - used) >= self.duration_minutes

    def deduct_membership_minutes(self):
        if self.has_remaining_minutes():
            self.membership.used_minutes += self.duration_minutes
            self.membership.save()

    # ---------------- Pricing & Offers ----------------
    def get_loyalty_profile(self):
        return LoyaltyProfile.objects.filter(user=self.user).first()

    def get_loyalty_discount(self):
        return self.loyalty.get_discount() if self.loyalty else 0

    def get_pricing(self):
        if not self.pricing_plan:
            return None
        return TableTypePricing.objects.filter(
            table_type=self.table.table_type,
            pricing_plan=self.pricing_plan
        ).first()

    def get_applicable_special_offer(self):
        offers = SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=self.start_time.date(),
            valid_to__gte=self.start_time.date()
        )
        for offer in offers:
            if str(self.start_time.isoweekday()) not in offer.weekdays:
                continue
            if offer.time_from and offer.time_to and not (offer.time_from <= self.start_time.time() <= offer.time_to):
                continue
            if not offer.apply_to_all and self.table not in offer.tables.all():
                continue
            return offer
        return None

    def get_pricing_plan(self):
        today = self.start_time.date()
        applicable_plans = PricingPlan.objects.filter(
            valid_from__lte=today
        ).filter(
            Q(valid_to__gte=today) | Q(valid_to__isnull=True)
        )

        for plan in applicable_plans:
            if plan.is_applicable(self.start_time):
                return plan

        return None

    # ---------------- Calculation ----------------
    def calculate_base_price(self):
        if not self.pricing:
            self.base_price = 0
            return

        full_half_hours = self.duration_minutes // 30
        remaining_minutes = self.duration_minutes % 30  # округлим вверх

        if remaining_minutes > 0:
            full_half_hours += 1

        if self.is_group:
            half_hour_rate = self.pricing.half_hour_rate_group or (self.pricing.hour_rate_group / 2)
        else:
            half_hour_rate = self.pricing.half_hour_rate or (self.pricing.hour_rate / 2)

        price = half_hour_rate * full_half_hours

        # Применяем скидки
        if self.special_offer:
            price *= (1 - self.special_offer.discount_percent / 100)

        if self.loyalty:
            price *= (1 - self.get_loyalty_discount() / 100)

        self.base_price = int(price)

    def calculate_equipment_price(self):
        if not self.equipment_items:
            self.equipment_price = 0
            return

        full_half_hours = self.duration_minutes // 30
        if self.duration_minutes % 30 > 0:
            full_half_hours += 1

        total = 0
        for item in self.equipment_items:
            equipment = item['equipment']
            quantity = item.get('quantity', 1)

            if hasattr(equipment, 'price_per_half_hour') and equipment.price_per_half_hour:
                unit_rate = equipment.price_per_half_hour
            else:
                unit_rate = equipment.price_per_hour / 2  # fallback

            eq_price = unit_rate * full_half_hours * quantity
            total += eq_price

        self.equipment_price = int(total)

    def calculate_total_price(self):
        self.calculate_base_price()
        self.calculate_equipment_price()
        self.total_price = self.base_price + self.equipment_price

    # ---------------- Booking Creation ----------------
    def create_booking(self):
        if not self.is_table_available():
            raise Exception("Стол уже забронирован на это время")

        self.calculate_total_price()

        # Списать минуты с абонемента, если можно
        if self.has_remaining_minutes():
            self.deduct_membership_minutes()
            status = 'confirmed'
        elif self.has_unlimited_membership():
            status = 'confirmed'
        else:
            status = 'pending'

        booking = Booking.objects.create(
            user=self.user,
            table=self.table,
            pricing=self.pricing,
            start_time=self.start_time,
            end_time=self.end_time,
            participants=self.participants,
            is_group=self.is_group,
            base_price=self.base_price,
            equipment_price=self.equipment_price,
            total_price=self.total_price,
            status=status
        )

        for item in self.equipment_items:
            BookingEquipment.objects.create(
                booking=booking,
                equipment=item['equipment'],
                quantity=item.get('quantity', 1)
            )

        return booking
