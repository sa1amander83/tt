import { html } from '../components.js';

export const WeekView = {
  render(data, store) {
    if (!data.days || !data.tables) return html`<div class="p-4 text-gray-500">Нет данных для отображения</div>`;

    const days = Object.entries(data.days).map(([date, day]) => ({ date, ...day }));

    const header = days.map(d => html`
      <div class="text-center p-3 bg-white rounded-lg shadow-sm border border-gray-200 font-medium">
        <div class="text-gray-600 text-sm">
          ${new Date(d.date).toLocaleDateString('ru-RU', { weekday: 'short' })}
        </div>
        <div class="text-lg font-semibold">
          ${new Date(d.date).toLocaleDateString('ru-RU', { day: 'numeric' })}
        </div>
      </div>`).join('');

    const body = data.tables.map(t => html`
      <div class="grid grid-cols-${days.length + 1} gap-3 mb-3">
        <div class="flex items-center justify-end bg-white p-3 rounded-lg shadow-sm border border-gray-200 font-medium text-gray-700">
          Стол #${t.number}
          ${t.table_type ? html`<span class="ml-2 text-xs text-gray-500">(${t.table_type})</span>` : ''}
        </div>
        ${days.map(d => this.dayCell(d, t, store)).join('')}
      </div>`).join('');

    return html`
      <div class="p-4">
        <div class="grid grid-cols-${days.length + 1} gap-3 mb-3">
          <div class="bg-transparent"></div>
          ${header}
        </div>
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

    if (!day.is_working_day) return html`
      <div class="flex items-center justify-center bg-gray-100 text-gray-400 rounded-lg p-3 h-full">
        <span class="text-xs">Закрыто</span>
      </div>`;

    if (isPast && !store.get().user?.isAdmin) return html`
      <div class="flex items-center justify-center bg-gray-50 text-gray-400 rounded-lg p-3 h-full">
        <span class="text-xs">Прошло</span>
      </div>`;

    const percent = total > 0 ? Math.round((booked / total) * 100) : 0;
    const cls = percent === 100 ? 'bg-red-100 text-red-800 border-red-200' :
               percent > 50 ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
               'bg-green-100 text-green-800 border-green-200';

    return html`
      <div class="flex flex-col items-center justify-center rounded-lg p-3 h-full border ${cls} transition-all hover:shadow-md cursor-pointer"
           data-date="${day.date}" data-table="${table.id}">
        <div class="text-sm font-medium">${booked}/${total}</div>
        <div class="w-full bg-white rounded-full h-1.5 mt-1">
          <div class="bg-current h-1.5 rounded-full" style="width: ${percent}%"></div>
        </div>
      </div>`;
  }
};