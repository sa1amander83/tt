import { html } from '../components.js';

export const MonthView = {
  render(data, store) {
    if (!data.weeks) return html`<div class="p-4 text-gray-500">Нет данных для отображения</div>`;

    const weeksHtml = data.weeks.map((week, weekIndex) => html`
      <div class="grid grid-cols-7 gap-2 mb-2">
        ${week.map((d, dayIndex) => this.dayBox(d, store, weekIndex, dayIndex)).join('')}
      </div>`).join('');

    return html`
      <div class="p-4">
        <div class="grid grid-cols-7 gap-2 mb-3 font-medium text-center text-gray-600 text-sm">
          <div>Понедельник</div>
          <div>Вторник</div>
          <div>Среда</div>
          <div>Четверг</div>
          <div>Пятница</div>
          <div>Суббота</div>
          <div>Воскресенье</div>
        </div>
        ${weeksHtml}
      </div>`;
  },

  dayBox(day, store, weekIndex, dayIndex) {
    if (!day || !day.date) return html`<div class="h-16"></div>`;

    const date = new Date(day.date);
    const isCurrentMonth = date.getMonth() === (store.get().currentDate?.getMonth() || new Date().getMonth());
    const today = new Date(); today.setHours(0,0,0,0);
    const isToday = date.toDateString() === today.toDateString();
    const isPast = date < today && !isToday;

    let cls = 'p-2 border rounded-lg h-16 flex flex-col transition-all';
    if (!isCurrentMonth) {
      cls += ' bg-gray-50 text-gray-400';
    } else if (!day.is_working_day) {
      cls += ' bg-red-50 text-red-600 border-red-100';
    } else if (day.shortened) {
      cls += ' bg-yellow-50 text-yellow-600 border-yellow-100';
    } else if (isToday) {
      cls += ' bg-blue-50 border-blue-200 text-blue-600 font-medium';
    } else if (isPast) {
      cls += ' bg-gray-100 text-gray-500';
    } else {
      cls += ' bg-white border-gray-200 hover:bg-gray-50 cursor-pointer';
    }

    const bookings = day.user_bookings_count || 0;
    const isWeekend = dayIndex >= 5; // Суббота и воскресенье

    return html`
      <div class="${cls}" data-date="${day.date}">
        <div class="flex justify-between items-start">
          <span class="text-sm">${date.getDate()}</span>
          ${isWeekend && isCurrentMonth ? html`<span class="text-xs text-gray-400">${dayIndex === 5 ? 'СБ' : 'ВС'}</span>` : ''}
        </div>
        ${bookings ? html`
          <div class="mt-auto flex justify-center">
            <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-medium">
              ${bookings}
            </span>
          </div>
        ` : ''}
      </div>`;
  }
};