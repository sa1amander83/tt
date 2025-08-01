import random
from datetime import datetime, timedelta, time, date

from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker

from accounts.models import User
from admin_settings.models import Table, Equipment
from bookings.models import  TableTypePricing, Booking, BookingEquipment
from pricing.models import PricingPlan
from django.utils.timezone import make_aware
fake = Faker('ru_RU')

def get_valid_booking_datetime(pricing_plans, year, month):
    """
    Генерирует случайный datetime для бронирования, который соответствует
    действующему тарифному плану и его расписанию.
    """
    possible_slots = []

    for plan in pricing_plans:
        try:
            valid_from = plan.valid_from
            valid_to = plan.valid_to or date(year + 1, 1, 1)

            # Пропускаем планы, которые не действуют в выбранном месяце
            if valid_from > date(year, month, 28) or valid_to < date(year, month, 1):
                continue

            weekdays = plan.weekdays or '1234567'
            valid_weekdays = set(weekdays)

            time_from = plan.time_from or time(8, 0)
            time_to = plan.time_to or time(22, 0)

            for day in range(1, 29):  # Ограничиваемся 28 днями
                current_date = date(year, month, day)
                if str(current_date.isoweekday()) not in valid_weekdays:
                    continue

                for hour in range(time_from.hour, time_to.hour):
                    for minute in [0, 30]:
                        naive_dt = datetime.combine(current_date, time(hour, minute))
                        aware_dt = make_aware(naive_dt)
                        possible_slots.append(aware_dt)

        except Exception as e:
            print(f"Ошибка в плане '{plan.name}': {e}")
            continue

    if not possible_slots:
        print("Нет подходящих таймслотов.")
        return None

    return random.choice(possible_slots)

def create_fake_users_and_bookings(num_users=10):
    tables = list(Table.objects.filter(is_active=True))
    pricings = list(TableTypePricing.objects.select_related('pricing_plan', 'table_type').all())

    equipment_list = [
        "Ракетки",
        "Мячи для КБМ",
        "Колёса для тренировки",
        "Робот"
    ]

    for name in equipment_list:
        Equipment.objects.get_or_create(
            name=name,
            defaults={
                "description": f"Описание для {name}",
                "price_per_half_hour": 200,
                "price_per_hour": 350,
                "is_available": True
            }
        )
    for i in range(num_users):
        phone = f'+7{random.randint(9000000000, 9999999999)}'
        email = fake.email()
        username = fake.first_name()
        age = random.randint(10, 60)

        user = User.objects.create_user(
            phone=phone,
            password='123',
            user_name=username,
            email=email,
            user_age=age
        )
        print(f"Создан пользователь: {user}")











    tables = list(Table.objects.filter(is_active=True))
    pricings = list(TableTypePricing.objects.select_related('pricing_plan', 'table_type').all())
    equipment_list = list(Equipment.objects.filter(is_available=True))
    pricing_plans = list(PricingPlan.objects.all())

    users = list(User.objects.all())

    for user in users:
        bookings_created_per_day = {}

        # 2 брони в прошлом месяце
        last_month_date = timezone.now().date().replace(day=1) - timedelta(days=1)
        last_month = last_month_date.month
        last_month_year = last_month_date.year

        for _ in range(2):
            for attempt in range(10):
                start_time = get_valid_booking_datetime(pricing_plans, last_month_year, last_month)
                if not start_time:
                    continue
                day_key = start_time.date()
                if bookings_created_per_day.get(day_key, 0) < 2:
                    break
            else:
                continue

            duration_minutes = random.choice([30, 60, 90, 120])
            end_time = start_time + timedelta(minutes=duration_minutes)

            table = random.choice(tables)
            pricing = random.choice(pricings)

            booking = Booking.objects.create(
                user=user,
                table=table,
                pricing=pricing,
                start_time=start_time,
                end_time=end_time,
                is_group=random.choice([True, False]),
                participants=random.randint(1, 5),
                status=random.choice(['pending', 'paid']),
                base_price=0,
                equipment_price=0,
                total_price=0,
            )

            # Добавление оборудования через промежуточную модель с количеством
            if equipment_list and random.choice([True, False]):
                selected_equipment = random.sample(equipment_list, k=random.randint(1, min(3, len(equipment_list))))
                for eq in selected_equipment:
                    quantity = random.randint(1, 3)
                    BookingEquipment.objects.create(
                        booking=booking,
                        equipment=eq,
                        quantity=quantity
                    )

            booking.calculate_prices()
            booking.save()
            bookings_created_per_day[day_key] = bookings_created_per_day.get(day_key, 0) + 1

            print(f"Создано бронирование в прошлом месяце для {user.phone} на {start_time}")

        # 3 брони в мае или июне 2025
        for _ in range(3):
            for attempt in range(10):
                month = random.choice([6,7,8])
                year = 2025
                start_time = get_valid_booking_datetime(pricing_plans, year, month)
                if not start_time:
                    continue
                day_key = start_time.date()
                if bookings_created_per_day.get(day_key, 0) < 2:
                    break
            else:
                continue

            duration_minutes = random.choice([30, 60, 90, 120])
            end_time = start_time + timedelta(minutes=duration_minutes)

            table = random.choice(tables)
            pricing = random.choice(pricings)

            booking = Booking.objects.create(
                user=user,
                table=table,
                pricing=pricing,
                start_time=start_time,
                end_time=end_time,
                is_group=random.choice([True, False]),
                participants=random.randint(1, 5),
                status=random.choice(['pending', 'paid']),
                base_price=0,
                equipment_price=0,
                total_price=0,
            )

            if equipment_list and random.choice([True, False]):
                selected_equipment = random.sample(equipment_list, k=random.randint(1, min(3, len(equipment_list))))
                for eq in selected_equipment:
                    quantity = random.randint(1, 3)
                    BookingEquipment.objects.create(
                        booking=booking,
                        equipment=eq,
                        quantity=quantity
                    )

            booking.calculate_prices()
            booking.save()
            bookings_created_per_day[day_key] = bookings_created_per_day.get(day_key, 0) + 1

            print(f"Создано бронирование в мае-июне 2025 для {user.phone} на {start_time}")


class Command(BaseCommand):
    help = 'Создаёт фейковых пользователей и бронирования'

    def handle(self, *args, **options):
        create_fake_users_and_bookings()