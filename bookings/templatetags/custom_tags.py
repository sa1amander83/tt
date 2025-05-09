from django import template

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