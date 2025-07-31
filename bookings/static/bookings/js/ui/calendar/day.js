import { html } from '../components.js';

export const DayView = {
  render(data, store) {
    if (!data.is_working_day)
      return html`<div class="p-8 text-center">Выходной день</div>`;

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
        ${tables.map(t => html`<div class="flex-1 p-2 text-center">Стол #${t.number}</div>`).join('')}
      </div>`;
  },

  slotCell(data, table, time) {
    const slot = data.day_schedule[table.id]?.[time] || {};
    const isPast = new Date(`${data.date}T${time}`) < new Date();
    const status = isPast ? 'past' : (slot.status || 'available');
    const cls = {
      available: 'bg-green-100 hover:bg-green-200',
      booked   : 'bg-red-100',
      past     : 'bg-gray-100 text-gray-400'
    };
    return html`
      <div class="flex items-center justify-center h-12 border-b ${cls[status]} ${status === 'available' ? 'cursor-pointer' : ''}"
           data-date="${data.date}" data-time="${time}" data-table="${table.id}">
        ${status === 'available' ? 'Свободно' : '-'}
      </div>`;
  }
};