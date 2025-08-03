import {html} from '../components.js';

export const DayView = {
    render(data, options) {
        const {store} = options;
        if (!data.is_working_day)
            return html`
                <div class="p-8 text-center">Выходной день</div>`;

        const rows = data.time_slots.map(time => {
            const cells = data.tables.map(t => this.slotCell(data, t, time, store));
            return html`
                <div class="flex border-b">
                    <div class="w-24 p-2 text-right">${time}</div>
                    <div class="flex-1 grid grid-cols-${data.tables.length}">
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
        const slot = data.day_schedule[table.id]?.[time] || {};
        const isPast = new Date(`${data.date}T${time}`) < new Date();
        const state = store.get();
        const user = state.user;

        const status = slot.status || 'available';
        let cls = '';
        let text = '';
        let clickable = false;

        // Определяем, идет ли бронирование сейчас
        const isCurrent = !isPast && status === 'processing';

        if (isPast) {
            // Прошедшее время
            switch (status) {
                case 'completed':
                    cls = 'bg-green-100 text-green-800 rounded-xl';
                    text = 'Завершено';
                    break;
                case 'processed':
                    cls = 'bg-red-200 text-red-800 rounded-xl';
                    text = 'Идет';
                    break;
                case 'cancelled':
                case 'expired':
                case 'returned':
                case 'available':
                    cls = 'bg-gray-200 text-gray-800 rounded-xl';
                    text = 'Свободен';
                    break;
                default:
                    cls = 'bg-gray-100 text-gray-800 rounded-xl';
                    text = '-';
            }
        } else {
            // Будущее время
            switch (status) {
                case 'processed':
                case 'pending':
                    cls = 'bg-red-500 text-white rounded-xl';
                    text = 'Ждет оплаты';
                    clickable = true;
                    break;
                case 'paid':
                    cls = 'bg-yellow-500 text-white rounded-xl';
                    text = 'Занят';
                    break;
                case 'cancelled':
                case 'expired':
                case 'returned':
                case 'available':
                    cls = 'bg-green-500 text-white rounded-xl';
                    text = 'Свободен';
                    clickable = true;
                    break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';
                    text = 'Свободен';
                    clickable = true;
            }
        }

        // Если бронирование идет сейчас, обновляем статус и цвет
        if (isCurrent) {
            cls = 'bg-blue-500 text-white rounded-xl';
            text = 'Идет сейчас';
        }

        return html`
            <div class="flex items-center justify-center h-12 border-b ${cls} ${(clickable || (user && user.is_staff)) ? 'cursor-pointer hover:opacity-90' : ''}"
                 data-date="${data.date}"
                 data-time="${time}"
                 data-table="${table.id}"
                 data-status="${status}"
                 data-booking-id="${slot.booking_id || ''}"
                 data-clickable="${clickable || (user && user.is_staff)}">
                ${text}
            </div>`;
    }
};