import { html } from '../components.js';

export const MonthView = {
  render(data, store) {
    if (!data.weeks) return html`<div>Нет данных</div>`;

    const weeksHtml = data.weeks.map(week => html`
      <div class="grid grid-cols-7 gap-2">
        ${week.map(d => this.dayBox(d, store)).join('')}
      </div>`).join('');

    return html`
      <div>
        <div class="grid grid-cols-7 gap-2 mb-2 font-medium text-center">
          Пн Вт Ср Чт Пт Сб Вс
        </div>
        ${weeksHtml}
      </div>`;
  },

  dayBox(day, store) {
    if (!day || !day.date) return html`<div></div>`;

    const date = new Date(day.date);
    const isCurrentMonth = date.getMonth() === (store.get().currentDate.getMonth());
    const today = new Date(); today.setHours(0,0,0,0);
    const isPast = date < today;

    let cls = 'p-2 border rounded text-sm';
    if (!isCurrentMonth) cls += ' bg-gray-100';
    else if (!day.is_working_day) cls += ' bg-red-50 text-red-700';
    else if (day.shortened) cls += ' bg-yellow-50 text-yellow-700';
    else if (+date === +today) cls += ' bg-blue-100';
    else cls += ' bg-white hover:bg-gray-50 cursor-pointer';

    const bookings = day.user_bookings_count || 0;
    return html`
      <div class="${cls}" data-date="${day.date}">
        <div class="font-medium">${date.getDate()}</div>
        ${bookings ? html`<div class="text-xs text-blue-600">${bookings}</div>` : ''}
      </div>`;
  }
};