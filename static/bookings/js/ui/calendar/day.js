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
    const username = slot.user?.name || '';

    let cls = '';
    let textTop = '';
    let textBottom = '';
    let clickable = false;

    const isUserBooking =
        user && !user.is_staff &&
        slot.user && slot.user.id === user.user_id &&
        ['pending', 'paid', 'completed', 'processing'].includes(status);

    const minutesSinceStart = (now - slotStart) / 60000;
    const isWithin5Minutes = minutesSinceStart >= 0 && minutesSinceStart <= 5;
    const isSlotPast = minutesSinceStart > 5 || now >= slotEnd;

    // === Для владельца брони ===
    if (isUserBooking) {
        cls = 'bg-red-900 text-white text-xl rounded-xl ring-4 ring-inset ring-amber-950';
        textTop = 'Ваша бронь';
        if (status === 'processing') textBottom = 'Идёт сейчас';
        else if (status === 'pending') textBottom = 'Ожидает оплаты';
        else if (status === 'paid') textBottom = 'Оплачено';
        else if (status === 'completed') textBottom = 'Завершено';
    }
    // === Для админа ===
    else if (user && user.is_staff) {
        if (isSlotPast) {
            // ПРОШЛОЕ
            switch (status) {
                case 'completed':
                    cls = 'bg-green-100 text-green-800 rounded-xl';
                    textBottom = 'Завершено';
                    textTop = username;
                    break;
                case 'cancelled':
                    cls = 'bg-red-100 text-red-800 rounded-xl';
                    textBottom = 'Отменено';
                    textTop = username;
                    break;
                case 'expired':
                    if (now < slotStart) {
                        // Слот в будущем, expired — считаем свободным
                        cls = 'bg-green-500 text-white rounded-xl';
                        textBottom = 'Свободен';
                        textTop = '';
                        clickable = true;
                    } else {
                        // Слот прошёл, expired — показываем как просрочено
                        cls = 'bg-gray-300 text-gray-900 rounded-xl';
                        textBottom = 'Просрочено';
                        textTop = username || '';
                    }
                    break;
                default:
                    cls = 'bg-gray-200 text-gray-800 rounded-xl';
                    textBottom = '—';
                    textTop = username || '';
            }
        } else {
            // БУДУЩЕЕ И НАСТОЯЩЕЕ
            switch (status) {
                case 'processing':
                    cls = 'bg-blue-500 text-white rounded-xl';
                    textBottom = 'Идёт сейчас';
                    textTop = username;
                    break;
                case 'pending':
                    cls = 'bg-yellow-500 text-white rounded-xl';
                    textBottom = 'Ожидает оплаты';
                    clickable = true;
                    textTop = username;
                    break;
                case 'paid':
                    cls = 'bg-red-500 text-white text-xl font-bold rounded-xl';
                    textBottom = 'Оплачено';
                    textTop = username;
                    break;
                case 'returned':
                    cls = 'bg-purple-200 text-purple-900 rounded-xl';
                    textBottom = 'Оплата возвращена';
                    textTop = username;
                    break;
                case 'expired':
                    // Если вдруг expired в будущем — показываем как свободный (доп. страховка)
                    cls = 'bg-green-500 text-white rounded-xl';
                    textBottom = 'Свободен';
                    clickable = true;
                    textTop = '';
                    break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';
                    textBottom = 'Свободен';
                    clickable = true;
                    textTop = '';
            }
        }
    }
    // === Для остальных пользователей ===
    else {
        if (status === 'processing') {
            cls = 'bg-blue-500 text-white rounded-xl';
            textBottom = 'Идёт сейчас';
        } else if (isSlotPast) {
            if (status === 'completed') {
                cls = 'bg-green-100 text-green-800 rounded-xl';
                textBottom = 'Завершено';
            } else {
                cls = 'bg-gray-200 text-gray-800 rounded-xl';
                textBottom = '—';
            }
        } else {
            switch (status) {
                case 'pending':
                    cls = 'bg-yellow-500 text-white rounded-xl';
                    textBottom = 'Ожидает оплаты';
                    clickable = true;
                    break;
                case 'paid':
                    cls = 'bg-red-300 text-white rounded-xl';
                    textBottom = 'Занят';
                    break;
                case 'expired':
                    // expired в будущем — считаем свободным
                    if (now < slotStart) {
                        cls = 'bg-green-500 text-white rounded-xl';
                        textBottom = 'Свободен';
                        clickable = true;
                    } else {
                        cls = 'bg-gray-200 text-gray-800 rounded-xl';
                        textBottom = '—';
                    }
                    break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';
                    textBottom = 'Свободен';
                    clickable = true;
            }
        }
    }

    if (!clickable && status === 'available' && isWithin5Minutes) {
        clickable = true;
    }

    return html`
        <div class="p-px">
            <div class="flex flex-col items-center justify-center h-12 w-full leading-tight text-center ${cls} ${(clickable || (user && user.is_staff)) ? 'cursor-pointer hover:opacity-90' : ''}"
                 data-date="${data.date}"
                 data-time="${time}"
                 data-table="${table.number}"
                 data-status="${status}"
                 data-booking-id="${bookingId || ''}"
                 data-clickable="${clickable || (user && user.is_staff)}">
                ${textTop ? `<div class="text-xs">${textTop}</div>` : ''}
                ${textBottom ? `<div class="text-xs">${textBottom}</div>` : ''}
            </div>
        </div>
    `;
}
};