from django.views.generic import TemplateView
from django.utils import timezone
from .models import Table, Booking


class BookingsView(TemplateView):
    template_name = 'bookings/bookings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now()
        context['tables'] = Table.objects.all()
        context['bookings'] = Booking.objects.filter(user=self.request.user).order_by('start_time')
        return context