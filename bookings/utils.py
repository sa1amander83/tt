

def get_applicable_pricing_plan(dt):
    from bookings.models import PricingPlan

    plans = PricingPlan.objects.filter(valid_from__lte=dt.date()).order_by('-valid_from')
    for plan in plans:
        if (not plan.valid_to or plan.valid_to >= dt.date()) and plan.is_applicable(dt):
            return plan

    # Попробовать план по умолчанию
    return PricingPlan.objects.filter(is_default=True).first()
