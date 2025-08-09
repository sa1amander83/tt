import {html} from '../components.js';

export const DayView = {
    render(data, store) {
        if (!data.is_working_day)
            return html`
                <div class="p-8 text-center">Выходной день</div>`;

        const rows = data.time_slots.map(time => {
            const cells = data.tables.map(t => this.slotCell(data, t, time, store));
            return html`
                <div class="flex border-b">
                    <div class="w-24 p-2 text-right">${time}</div>
                    <div class="flex-1 grid grid-cols-${data.tables.length} gap-px">
                        ${cells.join('')}
                    </div>
                </div>`;
        }).join('');

        return html`
            <div class="overflow-hidden border rounded">
                ${this.header(data.tables)}
                ${rows}
            </div>`;
    },

    header(tables) {
        return html`
            <div class="flex border-b bg-gray-50">
                <div class="w-24 p-2">Время</div>
                ${tables.map(t => html`
                    <div class="flex-1 p-2 text-center">Стол #${t.number}</div>`).join('')}
            </div>`;
    },

slotCell(data, table, time, store) {
    const slot = data.day_schedule[table.number]?.[time] || {};
    const state = store.get();
    const user = state.user;

    const now = new Date();
    const slotStart = new Date(`${data.date}T${time}`);
    const durationMinutes = slot.duration || 30;
    const slotEnd = new Date(slotStart.getTime() + durationMinutes * 60000);

    const bookingId = slot.booking_id || null;
    const status = slot.status || 'available';
    let cls = '';
    let text = '';
    let clickable = false;

    // --- Если бронь есть, ищем её полное время ---
    let bookingStart = slotStart;
    let bookingEnd = slotEnd;

    if (bookingId) {
        const allSlots = Object.entries(data.day_schedule[table.number] || {})
            .filter(([t, s]) => s.booking_id === bookingId)
            .map(([t, s]) => ({
                start: new Date(`${data.date}T${t}`),
                end: new Date(new Date(`${data.date}T${t}`).getTime() + (s.duration || 30) * 60000)
            }));

        if (allSlots.length) {
            bookingStart = new Date(Math.min(...allSlots.map(s => s.start.getTime())));
            bookingEnd = new Date(Math.max(...allSlots.map(s => s.end.getTime())));
        }
    }

    // --- Логика отображения ---
    const isPast = now >= bookingEnd;
    const isCurrentBooking = bookingId && status === 'paid' && now >= bookingStart && now < bookingEnd;

    if (isCurrentBooking) {
        cls = 'bg-blue-500 text-white rounded-xl';
        text = 'Идёт сейчас';
    } else if (isPast) {
        switch (status) {
            case 'completed':
                cls = 'bg-green-100 text-green-800 rounded-xl';
                text = 'Завершено';
                break;
            default:
                cls = 'bg-gray-200 text-gray-800 rounded-xl';
                text = '—';
        }
    } else {
        switch (status) {
            case 'processed':
            case 'pending':
                cls = 'bg-yellow-500 text-white rounded-xl';
                text = 'Ждёт оплаты';
                clickable = true;
                break;
            case 'paid':
                cls = 'bg-red-500 text-white rounded-xl';
                text = 'Занят';
                break;
            default:
                cls = 'bg-green-500 text-white rounded-xl';
                text = 'Свободен';
                clickable = true;
        }
    }

    // Убрали border-b, чтобы gap-px создавал ровные линии
    return html`
        <div class="p-px">
            <div class="flex items-center justify-center h-12 w-full ${cls} ${(clickable || (user && user.is_staff)) ? 'cursor-pointer hover:opacity-90' : ''}"
                 data-date="${data.date}"
                 data-time="${time}"
                 data-table="${table.number}"
                 data-status="${status}"
                 data-booking-id="${bookingId || ''}"
                 data-clickable="${clickable || (user && user.is_staff)}">
                ${text}
            </div>
        </div>
    `;
}
};