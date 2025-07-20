from django import template
from datetime import datetime
register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Вернём None, если dictionary не словарь (например, если предыдущий get_item вернул None)
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_schedule_value(schedule, args):
    table_id, hour = args
    return schedule.get((table_id, hour))


@register.filter
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

@register.filter
def short_ru_day(value):
    days = {
        0: 'Пн',
        1: 'Вт',
        2: 'Ср',
        3: 'Чт',
        4: 'Пт',
        5: 'Сб',
        6: 'Вс',
    }
    return days.get(value.weekday(), '')


@register.filter
def get_item(dictionary, key):
    """Получение элемента из словаря"""
    return dictionary.get(key, {})

@register.filter
def is_past(value):
    """Проверяет, прошло ли уже указанное время"""
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return dt < datetime.now()
    except:
        return False

@register.filter
def concat(value, arg):
    """Конкатенация строк"""
    return f"{value}{arg}"

@register.filter
def get_item(dictionary, key):
    """Получение элемента из словаря"""
    return dictionary.get(key, {})