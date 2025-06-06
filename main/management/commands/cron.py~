from django.core.management.base import BaseCommand
from bookings.tasks import test_print_task

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        test_print_task.delay("From management command")
        self.stdout.write("Task dispatched")