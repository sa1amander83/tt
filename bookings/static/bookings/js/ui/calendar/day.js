import {html} from '../components.js';

export const DayView = {
    render(data, store) {
        if (!data.is_working_day)
            return html`
                <div class="p-8 text-center">Выходной день</div>`;

        const rows = data.time_slots.map(time => {
            const cells = data.tables.map(t => this.slotCell(data, t, time));
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

    slotCell(data, table, time) {

        const slot = data.day_schedule[table.id]?.[time] || {};
        const isPast = new Date(`${data.date}T${time}`) < new Date();

        // Определяем статус и цвет
        const status = slot.status || 'available';
        let cls = '';
        let text = '';

        if (isPast) {
            // Прошедшее время
            switch (status) {

                case 'completed':
                    cls = 'bg-green-100 text-green-800  rounded-xl'; // бледно-зелёный
                    text = 'Завершено';
                    break;

                case 'processing':
                    cls = 'bg-red-200 text-red-800  rounded-xl';    // бледно-красный
                    text = 'Идет';
                    break;
                case 'cancelled':
                case 'expired':
                case 'returned':
                    cls = 'bg-green-100 text-green-800  rounded-xl'; // бледно-зелёный
                    text = '-';
                    break;
                default:
                    cls = 'bg-green-100 text-green-800  rounded-xl'; // бледно-зелёный
                    text = '-';
            }
        } else {
            // Будущее время
            switch (status) {
                case 'processing':
                case 'pending':
                    cls = 'bg-red-500 text-white  rounded-xl';       // ярко-красный
                    text = 'Ожидает оплаты';
                    break;
                case 'paid':
                    cls = 'bg-yellow-500   rounded-xl text-white';     // ярко-зелёный
                    text = 'Оплачено';
                    break;
                // case 'cancelled':
                // case 'expired':
                // case 'returned':
                //   cls = 'bg-gray-300 text-gray-800  rounded-xl';   // серый
                //   text = 'Отменено/Просрочено/Возвращено';
                //   break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';     // ярко-зелёный
                    text = 'Свободен';
            }
        }

        return html`
            <div class="flex items-center justify-center h-12 border-b ${cls} ${!isPast && status === 'available' ? 'cursor-pointer' : ''}"
                 data-date="${data.date}" data-time="${time}" data-table="${table.id}">
                ${text}
            </div>`;
    }
};