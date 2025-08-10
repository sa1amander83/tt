// поправь путь, если нужно

import {CalendarUI} from "../../../bookings/js/ui/calendar/index.js";

export async function cancelBooking(bookingId) {
    if (!confirm('Вы уверены, что хотите отменить бронирование?')) return;

    try {
        const response = await fetch(`/bookings/api/cancel/${bookingId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при отмене бронирования');
        }

        const result = await response.json();
        if (result.success) {
            showNotification('Бронирование успешно отменено', 'success');
            if (CalendarUI && CalendarUI.store) {
                await CalendarUI.render();
            } else {
                // fallback: просто перезагружаем таблицу
                location.reload();
            }

            // await UserBookings.render();
        } else {
            throw new Error(result.error || 'Неизвестная ошибка');
        }
    } catch (error) {
        console.error('Ошибка отмены бронирования:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

window.cancelBooking = cancelBooking;