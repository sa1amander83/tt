from django.core.management.base import BaseCommand
from datetime import time, timedelta
from django.utils.timezone import now
from random import randint, choice

from admin_settings.models import WorkingDay, SpecialOffer
from bookings.models import TableType, Table, PricingPlan, TableTypePricing


class Command(BaseCommand):
    help = "Создает начальные данные для клуба: типы столов, столы, тарифы и спецпредложения"

    def handle(self, *args, **options):
        self.setup_club()
        self.stdout.write(self.style.SUCCESS("Настройки клуба успешно созданы."))

    def setup_club(self):
        table_type_names = ['Детский', 'Стандартный', 'Профи', 'Робот']
        table_types = {}
        for name in table_type_names:
            table_type, _ = TableType.objects.get_or_create(name=name, defaults={
                'description': f'{name} тип стола',
                'max_capacity': randint(2, 6)
            })
            table_types[name] = table_type

        table_config = [
            ('Детский', 1),
            ('Стандартный', 3),
            ('Профи', 3),
            ('Робот', 1)
        ]

        table_number = 1
        for type_name, count in table_config:
            for _ in range(count):
                Table.objects.get_or_create(number=table_number, defaults={
                    'table_type': table_types[type_name],
                    'is_active': True,
                    'description': f'Стол #{table_number} ({type_name})'
                })
                table_number += 1

        for weekday in range(7):  # 0 = Пн ... 6 = Вс
            is_weekend = weekday >= 5
            WorkingDay.objects.update_or_create(day=weekday, defaults={
                'is_open': True,
                'open_time': time(8 if is_weekend else 9, 0),
                'close_time': time(23, 0)
            })

        pricing_plans_info = [
            ('Утро', 9, 12, '12345'),
            ('День', 12, 17, '12345'),
            ('Вечер', 17, 23, '12345'),
            ('Выходные', 8, 23, '67')
        ]

        today = now().date()
        pricing_plans = {}
        for name, start_hour, end_hour, weekdays in pricing_plans_info:
            plan, _ = PricingPlan.objects.get_or_create(name=name, defaults={
                'description': f'Тариф "{name}"',
                'is_default': False,
                'valid_from': today,
                'time_from': time(start_hour, 0),
                'time_to': time(end_hour, 0),
                'weekdays': weekdays
            })
            pricing_plans[name] = plan

        all_plans = list(PricingPlan.objects.all())
        all_types = list(TableType.objects.all())

        for _ in range(10):
            plan = choice(all_plans)
            table_type = choice(all_types)
            TableTypePricing.objects.update_or_create(
                pricing_plan=plan,
                table_type=table_type,
                defaults={
                    'hour_rate': randint(300, 500),
                    'half_hour_rate': randint(150, 300),
                    'hour_rate_group': randint(400, 700),
                    'min_duration': 30,
                    'max_duration': 180
                }
            )

        SpecialOffer.objects.get_or_create(
            name='Скидка 10% на утренние занятия',
            defaults={
                'description': 'Действует до 12:00 на все столы',
                'discount_percent': 10,
                'is_active': True,
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
                'weekdays': '1234567',
                'time_from': time(0, 0),
                'time_to': time(12, 0),
                'apply_to_all': True
            }
        )

        SpecialOffer.objects.get_or_create(
            name='15% скидка в пятницу на последние 2 часа',
            defaults={
                'description': 'Действует по пятницам с 21:00 до закрытия',
                'discount_percent': 15,
                'is_active': True,
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
                'weekdays': '5',
                'time_from': time(21, 0),
                'time_to': time(23, 0),
                'apply_to_all': True
            }
        )
