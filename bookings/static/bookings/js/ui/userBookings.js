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

const rows = bookings.map((b, idx) => {
    const startLocal = addMoscowOffset(b.date, b.start);
    const endLocal = addMoscowOffset(b.date, b.end);

    const now = new Date();
    const minutesUntilStart = diffMinutes(now, startLocal);
    const canCancel = (minutesUntilStart >= this.minTimeToCancel) && (b.status === 'pending' || b.status === 'paid');
    const isOngoing = b.status === 'paid' && now >= startLocal && now <= endLocal;

    let statusText = statusTranslations[b.status] || b.status;
    let actionsHtml = '';

    if (isOngoing) {
        // Если сейчас идёт оплаченная бронь — показываем в статусе
        statusText = 'Оплачено / Идет сейчас';
        // В действиях ничего не показываем
    } else {
        // Иначе показываем кнопки если надо
        if (b.status === 'pending') {
            actionsHtml += `<button class="text-blue-600 hover:underline" data-id="${b.id}">Оплатить</button>`;
        }
        if (canCancel) {
            actionsHtml += `<button class="text-red-600 hover:underline" data-id="${b.id}">Отменить</button>`;
        }
    }

    return `
<tr class="hover:bg-gray-50 transition-colors">
  <td class="border border-gray-300 px-4 py-2">${idx + 1}</td>
  <td class="border border-gray-300 px-4 py-2">${b.date}</td>
  <td class="border border-gray-300 px-4 py-2">${startLocal.toTimeString().slice(0,5)}–${endLocal.toTimeString().slice(0,5)}</td>
  <td class="border border-gray-300 px-4 py-2">#${b.table_number}</td>
  <td class="border border-gray-300 px-4 py-2">${statusText}</td>
  <td class="border border-gray-300 px-4 py-2 space-x-2">${actionsHtml}</td>
</tr>`;
});

        container.innerHTML = `
<div class="overflow-x-auto">
  <table class="w-full border border-gray-300 text-sm text-center rounded-lg overflow-hidden shadow-md">
    <thead class="bg-gray-100 text-gray-700 uppercase">
      <tr>
        <th class="border border-gray-300 px-4 py-2">№</th>
        <th class="border border-gray-300 px-4 py-2">Дата</th>
        <th class="border border-gray-300 px-4 py-2">Время</th>
        <th class="border border-gray-300 px-4 py-2">Стол</th>
        <th class="border border-gray-300 px-4 py-2">Статус</th>
        <th class="border border-gray-300 px-4 py-2">Действия</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200">
  ${rows.join('')}
    </tbody>
  </table>
</div>`;

        container.querySelectorAll('button').forEach(btn =>
            btn.addEventListener('click', async e => {
                const bookingId = e.target.dataset.id;
                const action = e.target.textContent.trim();

                const {BookingAPI} = await import('../api/booking.js');
                if (action === 'Оплатить') {
                    BookingAPI.payment(bookingId)
                        .then(() => this.render())
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
