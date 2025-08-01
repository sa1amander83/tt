import { $ } from '../utils/dom.js';
import { CalendarAPI } from '../api/calendar.js';
import { formatDate } from '../utils/date.js';
export const UserBookings = {
  store: null,
  init(store) {
    this.store = store;
    store.subscribe(() => this.render());
       const { user } = this.store.get();
    if (!user) return;
    this.render();
  },

  async render() {
    const container = $('#user-bookings-container');
    if (!container) return;

    const { user, currentDate, currentView } = this.store.get();
    if (!user) return (container.innerHTML = 'Войдите для просмотра');

    const dateParam = currentView === 'week'
      ? window.utils.getMonday(currentDate)
      : currentDate;

    const params = { date: formatDate(dateParam), view: currentView };
    const data = await CalendarAPI.data(params);

    const bookings = data.user_bookings || [];
    if (!bookings.length) {
      container.innerHTML = `<div class="text-gray-500">Нет бронирований</div>`;
      return;
    }

    const rows = bookings.map(b => `
      <tr>
        <td class="border p-2">${b.date}</td>
        <td class="border p-2">${b.start}–${b.end}</td>
        <td class="border p-2">#${b.table_number}</td>
        <td class="border p-2">${b.status}</td>
        <td class="border p-2">
          ${b.status === 'ожидает оплаты'
            ? `<button class="text-blue-600">Оплатить</button>`
            : ''}
          ${b.status !== 'отменено'
            ? `<button class="text-red-600" onclick="BookingAPI.cancel(${b.id})">Отменить</button>`
            : ''}
        </td>
      </tr>`).join('');

    container.innerHTML = `
      <table class="w-full border text-sm">
        <thead class="bg-gray-100">
          <tr><th>Дата</th><th>Время</th><th>Стол</th><th>Статус</th><th>Действия</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>`;
  }
};