from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse
from yookassa import Payment

from bookings.models import Booking, TimeSlot
from .models import  Tables
from .forms import BookingForm


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/bookings_table.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.for_user(self.request.user)


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_modal.html'
    context_object_name = 'booking'



class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/bookings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Tables.objects.all()
        return context


def available_slots(request):
    table_id = request.GET.get('table')
    date = request.GET.get('date')

    try:
        table = Tables.objects.get(pk=table_id)
        slots = TimeSlot.objects.available_slots(table, date)
        data = [{
            'start': slot.start_time.strftime('%H:%M'),
            'end': slot.end_time.strftime('%H:%M'),
            'price': str(slot.price)
        } for slot in slots]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


class PaymentHandlerView(View):
    def post(self, request, *args, **kwargs):
        try:
            event = Booking.objects.get(pk=kwargs['pk'], user=request.user)
            payment = Payment.create({
                "amount": {
                    "value": str(event.total_cost),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": request.build_absolute_uri(
                        reverse('payment-callback', kwargs={'pk': event.pk})
                    )
                },
                "capture": True,
                "description": f"Бронирование стола #{event.table.number}"
            })
            event.payment_id = payment.id
            event.save()
            return JsonResponse({'confirmation_url': payment.confirmation.confirmation_url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class PaymentCallbackView(View):
    def get(self, request, *args, **kwargs):
        event = Booking.objects.get(pk=kwargs['pk'])
        if event.update_payment_status():
            return redirect('booking-detail', pk=event.pk)
        return redirect('payment-error')