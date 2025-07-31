import { html } from '../components.js';

export const WeekView = {
  render(data, store) {
    if (!data.days || !data.tables) return html`<div>Нет данных</div>`;

    const days = Object.entries(data.days).map(([date, day]) => ({ date, ...day }));
    const header = days.map(d => html`
      <div class="text-center p-2 bg-white rounded">
        ${new Date(d.date).toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' })}
      </div>`).join('');

    const body = data.tables.map(t => html`
      <div class="grid grid-cols-${days.length + 1} gap-2">
        <div class="bg-white p-2 text-right font-medium">Стол #${t.number}</div>
        ${days.map(d => this.dayCell(d, t, store)).join('')}
      </div>`).join('');

    return html`
      <div>
        <div class="grid grid-cols-${days.length + 1} gap-2 mb-2">${header}</div>
        ${body}
      </div>`;
  },

  dayCell(day, table, store) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const isPast = new Date(day.date) < today;
    const total = Object.keys(day.day_schedule?.[table.id] || {}).length;
    const booked = Object.values(day.day_schedule?.[table.id] || {})
                         .filter(s => s.status !== 'available').length;

    if (!day.is_working_day) return html`<div class="bg-gray-100 text-center">–</div>`;
    if (isPast && !store.get().user?.isAdmin) return html`<div class="bg-gray-100 text-center">–</div>`;

    const cls = booked === total ? 'bg-red-100' : (booked ? 'bg-yellow-100' : 'bg-green-100');
    return html`
      <div class="text-center p-2 rounded ${cls} cursor-pointer"
           data-date="${day.date}" data-table="${table.id}">
        ${booked}/${total}
      </div>`;
  }
};