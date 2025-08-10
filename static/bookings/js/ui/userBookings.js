import {CalendarAPI} from '../api/calendar.js';
import {formatDate, getMonday} from '../utils/date.js';

const $ = window.jQuery;

const monthsGenitive = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
];

const monthsAccusative = [
    'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
    'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
];

function formatHeaderDate(date, view) {
    const d = new Date(date);

    if (view === 'week') {
        const mon = getMonday(d);
        const sun = new Date(mon);
        sun.setDate(mon.getDate() + 6);
        return `${mon.getDate()} – ${sun.getDate()} ${monthsGenitive[sun.getMonth()]} ${sun.getFullYear()}`;
    }
    if (view === 'month') {
        return `${monthsAccusative[d.getMonth()]} ${d.getFullYear()}`;
    }
    return `${d.getDate()} ${monthsGenitive[d.getMonth()]} ${d.getFullYear()}`;
}

function addMoscowOffset(dateStr, timeStr) {
    // Без Z, создаём дату из строки, предположим, что время локальное в Москве (UTC+3)
    const dt = new Date(`${dateStr}T${timeStr}:00`);
    // Проверим часовой пояс, если нужно, можно сдвинуть вручную, но скорее всего не нужно
    return dt;
}

// Возвращает разницу в минутах между date2 и date1 (date2 - date1)
function diffMinutes(date1, date2) {
    return (date2 - date1) / 60000;
}

function syncHeaderDate(store) {
    const {currentDate, currentView} = store.get();
    $('#bookings-period-display').text(formatHeaderDate(currentDate, currentView));
}

export const UserBookings = {
    store: null,
    minTimeToCancel: 10,  // дефолтное значение на случай ошибки

    async fetchMinTimeToCancel() {
        try {
            const res = await fetch('/settings/get_min_time_to_cancel/');
            if (!res.ok) throw new Error('Ошибка получения настроек');
            const data = await res.json();
            this.minTimeToCancel = Number(data.min_time_to_cancel) || 10;
        } catch (e) {
            console.warn('Не удалось получить min_time_to_cancel, используем значение по умолчанию', e);
        }
    },

    async init(store) {
        this.store = store;
        await this.fetchMinTimeToCancel(); // получаем настройки перед рендером
        syncHeaderDate(store);
        store.subscribe(() => {
            syncHeaderDate(store);
            this.render();
        });
        this.render();
    },

    async render() {
        const container = document.querySelector('#user-bookings-container');
        if (!container) return;

        const {user, currentDate, currentView} = this.store.get();
        if (!currentDate) return;
        if (!user) {
            container.innerHTML = 'Войдите для просмотра';
            return;
        }

        const dates = [];
        if (currentView === 'week') {
            const mon = getMonday(currentDate);
            for (let i = 0; i < 7; i++) {
                const d = new Date(mon);
                d.setDate(mon.getDate() + i);
                dates.push(formatDate(d));
            }
        } else if (currentView === 'month') {
            const y = currentDate.getFullYear();
            const m = currentDate.getMonth();
            const days = new Date(y, m + 1, 0).getDate();
            for (let d = 1; d <= days; d++) {
                dates.push(formatDate(new Date(y, m, d)));
            }
        } else {
            dates.push(formatDate(currentDate));
        }

        let bookings = [];
        try {
            for (const date of dates) {
                const data = await CalendarAPI.data({date, view: 'day'});
                bookings = bookings.concat(data.user_bookings || []);
            }
        } catch (e) {
            console.error('Error loading bookings:', e);
            container.innerHTML = '<div class="text-red-500">Ошибка загрузки бронирований</div>';
            return;
        }

        if (!bookings.length) {
            container.innerHTML = '<div class="text-gray-500">Нет бронирований</div>';
            return;
        }

        const statusTranslations = {
            pending: 'Ожидает оплаты',
            paid: 'Оплачено',
            cancelled: 'Отменено',
            completed: 'Завершено',
            processing: 'Идет',
            expired: 'Истекло',
            available: 'Свободен'
        };

        const now = new Date();
        const isAdmin = user?.is_staff || user?.role === 'admin';
        const rows = bookings.map((b, idx) => {
            const startLocal = addMoscowOffset(b.date, b.start);
            const endLocal = addMoscowOffset(b.date, b.end);
            const minutesUntilStart = diffMinutes(now, startLocal);

            const canCancel = (isAdmin || (minutesUntilStart >= this.minTimeToCancel)) && (b.status === 'pending' || b.status === 'paid');
            const isOngoing = b.status === 'paid' && now >= startLocal && now <= endLocal;

            let statusText = statusTranslations[b.status] || b.status;
            let actionsHtml = '';

            if (isOngoing) {
                statusText = 'Оплачено / Идет сейчас';
            } else {
                if (b.status === 'pending') {
                    actionsHtml += `
 <button class="px-3 py-1 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition mr-2"
          data-id="${b.id}">
      Оплатить
  </button>`;
                }
                if (canCancel) {
                    actionsHtml += `
  <button class="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition"
          data-id="${b.id}">
      Отменить
  </button>`;
                }
            }

            // Дополнительная ячейка для админа
           // const adminInfo = isAdmin ? `<td class="px-6 py-4 text-center whitespace-nowrap">${b.user || b.email || ''}<br>${b.user_phone || ''}</td>` : '';

            return `
<tr class="bg-white border-b hover:bg-gray-50 text-center">
  <td class="px-6 py-4 text-center">${idx + 1}</td>
  <td class="px-6 py-4 text-center">${b.date}</td>
  <td class="px-6 py-4 text-center">${startLocal.toTimeString().slice(0, 5)}–${endLocal.toTimeString().slice(0, 5)}</td>

  <td class="px-6 py-4 text-center">#${b.table_number}</td>
  <td class="px-6 py-4 text-center">${statusText}</td>
  <td class="px-6 py-4 text-center">${actionsHtml}</td>

</tr>`;
        });

        container.innerHTML = `
<div class="overflow-x-auto shadow-md sm:rounded-lg">
  <table class="w-full text-sm text-gray-500 stripe text-center " id="userBookingsTable">
    <thead class="text-xs text-gray-700 uppercase bg-gray-50 text-center ">
      <tr class=" ">
        <th scope="col" class="px-6 py-3  ">№</th>
        <th scope="col" class="px-6 py-3  ">Дата</th>
        <th scope="col" class="px-6 py-3  ">Время</th>
   
        <th scope="col" class="px-6 py-3  ">Стол</th>
        <th scope="col" class="px-6 py-3  ">Статус</th>
        <th scope="col" class="px-6 py-3  ">Действия</th>
      </tr>
    </thead>
    <tbody>
      ${rows.join('')}
    </tbody>
  </table>
</div>`;
// После container.innerHTML = ...;
        if ($.fn.DataTable.isDataTable('#userBookingsTable')) {
            $('#userBookingsTable').DataTable().destroy();
        }

        $('#userBookingsTable').DataTable({
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.5/i18n/ru.json'
            },
            paging: true,
            searching: false,
            ordering: true,
            order: [[1, 'asc']]  // сортировка по дате по умолчанию
        });

        container.querySelectorAll('button').forEach(btn =>
            btn.addEventListener('click', async e => {
                const bookingId = e.target.dataset.id;
                const action = e.target.textContent.trim();

                const {BookingAPI} = await import('../api/booking.js');

                if (action === 'Оплатить') {
                    BookingAPI.payment(bookingId)
                        .then(res => {
                            if (res.status === 'paid') {
                                this.render();
                            } else if (res.confirmation_url) {
                                window.open(res.confirmation_url, '_blank');
                            } else {
                                console.warn('Неожиданный ответ от сервера:', res);
                            }
                        })
                        .catch(err => console.error('Payment failed:', err));
                } else if (action === 'Отменить') {
                    BookingAPI.cancel(bookingId)
                        .then(() => this.render())
                        .catch(err => console.error('Cancellation failed:', err));
                }
            })
        );
    }
};
