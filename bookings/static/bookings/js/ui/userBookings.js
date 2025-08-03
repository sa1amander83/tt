import { $ } from '../utils/dom.js';
import { CalendarAPI } from '../api/calendar.js';
import { formatDate, getMonday } from '../utils/date.js';

export const UserBookings = {
  store: null,

  init(store) {
    this.store = store;
    store.subscribe(() => this.render());
    this.render();
  },

  async render() {
    const container = $('#user-bookings-container');
    if (!container) return;

    const { user, currentDate, currentView } = this.store.get();
    if (!user) return container.innerHTML = 'Войдите для просмотра';

    let dateParam;
    if (currentView === 'week') {
      const startOfWeek = getMonday(currentDate);
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(endOfWeek.getDate() + 6); // конец недели (воскресенье)
      dateParam = {
        start: formatDate(startOfWeek),
        end: formatDate(endOfWeek)
      };
    } else {
      dateParam = formatDate(currentDate);
    }

    const params = { date: dateParam, view: currentView };
    const data = await CalendarAPI.data(params);

    const bookings = data.user_bookings || [];
    if (!bookings.length) {
      container.innerHTML = `<div class="text-gray-500">Нет бронирований</div>`;
      return;
    }

    // Объект для перевода статусов на русский
    const statusTranslations = {
      'pending': 'Ожидает оплаты',
      'paid': 'Оплачено',
      'cancelled': 'Отменено',
      'completed': 'Завершено',
      'processing': 'Идет',
      'expired': 'Истекло',
      'available': 'Свободен'
    };

    const rows = bookings.map(b => `
      <tr>
        <td class="border p-2">${b.date}</td>
        <td class="border p-2">${b.start}–${b.end}</td>
        <td class="border p-2">#${b.table_number}</td>
        <td class="border p-2">${statusTranslations[b.status] || b.status}</td>
        <td class="border p-2">
          ${b.status === 'pending'
            ? `<button class="text-blue-600" data-id="${b.id}">Оплатить</button>`
            : ''}
          ${b.status !== 'cancelled'
            ? `<button class="text-red-600" data-id="${b.id}">Отменить</button>`
            : ''}
        </td>
      </tr>
    `).join('');

    container.innerHTML = `
      <table class="w-full border text-sm">
        <thead class="bg-gray-100">
          <tr><th>Дата</th><th>Время</th><th>Стол</th><th>Статус</th><th>Действия</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;

    // Добавляем обработчики событий для кнопок
    container.querySelectorAll('button').forEach(button => {
      button.addEventListener('click', async (e) => {
        const bookingId = e.target.dataset.id;
        const action = e.target.textContent.trim();

        if (action === 'Оплатить') {
          import('../api/booking.js').then(({ BookingAPI }) => {
            BookingAPI.payment(bookingId).then(response => {
              console.log('Payment successful:', response);
              this.render(); // Обновляем список бронирований
            }).catch(error => {
              console.error('Payment failed:', error);
            });
          });
        } else if (action === 'Отменить') {
          import('../api/booking.js').then(({ BookingAPI }) => {
            BookingAPI.cancel(bookingId).then(response => {
              console.log('Booking cancelled:', response);
              this.render(); // Обновляем список бронирований
            }).catch(error => {
              console.error('Cancellation failed:', error);
            });
          });
        }
      });
    });
  }
};