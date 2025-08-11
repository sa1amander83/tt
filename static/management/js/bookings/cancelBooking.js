import { CalendarUI } from "../../../bookings/js/ui/calendar/index.js";
import { getCSRFToken } from "../../../bookings/js/utils/getcsrf.js";

export async function cancelBooking(bookingId) {
    if (!confirm('Вы уверены, что хотите отменить бронирование?')) return;

    try {
        const response = await fetch(`/bookings/api/cancel/${bookingId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken// исправлено: вызов функции
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка при отмене бронирования');
        }

        const result = await response.json();
        if (result.success) {
            // уведомление
            if (typeof showNotification === 'function') {
                showNotification('Бронирование успешно отменено', 'success');
            } else {
                console.log('Бронирование успешно отменено');
            }

            // закрыть модалку (замени closeModal на свою функцию)
            if (typeof closeModal === 'function') {
                closeModal();
            } else {
                const modal = document.querySelector('.booking-modal');
                if (modal) modal.remove();
            }

            // обновить календарь
            if (CalendarUI && CalendarUI.store) {
                await CalendarUI.render();
            } else {
                location.reload();
            }
        } else {
            throw new Error(result.error || 'Неизвестная ошибка');
        }
    } catch (error) {
        console.error('Ошибка отмены бронирования:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Ошибка: ${error.message}`, 'error');
        }
    }
}

window.cancelBooking = cancelBooking;
