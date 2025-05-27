


def calculate_booking_price(pricing, duration_minutes, is_group, equipment_data):
    from .models import Equipment

    full_half_hours = duration_minutes // 30
    if duration_minutes % 30 > 0:
        full_half_hours += 1

    base_price = 0
    equipment_price = 0
    equipment_items = []

    # 1. Базовая цена
    if pricing:
        if is_group:
            rate = pricing.half_hour_rate_group or (pricing.hour_rate_group / 2)
        else:
            rate = pricing.half_hour_rate or (pricing.hour_rate / 2)

        base_price = rate * full_half_hours

    # 2. Оборудование
    for item in equipment_data:
        try:
            eq = Equipment.objects.get(id=item['id'], is_available=True)
            qty = int(item.get('quantity', 1))

            unit_rate = eq.price_per_half_hour if hasattr(eq,
                                                          'price_per_half_hour') and eq.price_per_half_hour else eq.price_per_hour / 2
            eq_price = unit_rate * full_half_hours * qty
            equipment_price += eq_price

            equipment_items.append({
                'id': eq.id,
                'name': eq.name,
                'quantity': qty,
                'price_per_half_hour': getattr(eq, 'price_per_half_hour', None),
                'price_per_hour': eq.price_per_hour,
                'total_price': int(eq_price),
            })
        except Equipment.DoesNotExist:
            continue

    total_price = int(base_price + equipment_price)

    return int(base_price), int(equipment_price), total_price, equipment_items


def get_applicable_pricing_plan(dt):
    from bookings.models import PricingPlan
    """Возвращает подходящий тарифный план на заданный datetime"""
    plans = PricingPlan.objects.filter(valid_from__lte=dt.date()).order_by('-valid_from')
    for plan in plans:
        if (not plan.valid_to or plan.valid_to >= dt.date()) and plan.is_applicable(dt):
            return plan
    return None