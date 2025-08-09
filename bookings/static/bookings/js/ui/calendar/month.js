import {html} from '../components.js';

export const MonthView = {
    render(data, store) {
        if (!data.weeks) return html`
            <div class="p-4 text-gray-500">Нет данных для отображения</div>`;

        const weeksHtml = data.weeks.map((week, weekIndex) => html`
            <div class="grid grid-cols-7 gap-2 mb-2">
                ${week.map((d, dayIndex) => this.dayBox(d, store, weekIndex, dayIndex)).join('')}
            </div>`).join('');

        return html`
            <div class="p-4">
                <div class="grid grid-cols-7 gap-2 mb-3 font-medium text-center text-gray-600 text-sm border-2">
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
    bindDayClicks(store) {
        // Снимаем старые обработчики
        document.querySelectorAll('#month-view-container [data-date]').forEach(el => {
            el.onclick = null;
        });

        // Добавляем обработчик клика
        document.querySelectorAll('#month-view-container [data-date]').forEach(el => {
            el.addEventListener('click', () => {
                const dateStr = el.getAttribute('data-date');
                if (!dateStr) return;

                const date = new Date(dateStr);
                store.set({
                    currentView: 'day',
                    currentDate: date
                });
            });
        });
    },
    dayBox(day, store, weekIndex, dayIndex) {
        if (!day || !day.date) return html`
            <div class="h-20"></div>`;

        const date = new Date(day.date);
        const currentMonth = store.get().currentDate?.getMonth() ?? new Date().getMonth();
        const isCurrentMonth = date.getMonth() === currentMonth;

        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const isToday = date.toDateString() === today.toDateString();
        const isPast = date < today && !isToday;

        const isAdmin = !!store.get().user?.is_staff;
        const bookings = day.user_bookings_count || 0;
        const isWeekend = dayIndex >= 5; // 5 = СБ, 6 = ВС (нумерация от Пн)
        const clubClosed = !day.is_working_day; // выходной клуба
        const isHoliday = !!day.is_holiday;     // (если бэк отдаёт)
        const shortened = !!day.shortened;

        // Приоритет фона: clubClosed > isHoliday > shortened > isToday > weekend > default
        let bgClass = 'bg-white';
        let textClass = 'text-gray-700';
        let borderClass = 'border-gray-200 border-2';

        if (!isCurrentMonth) {
            bgClass = 'bg-gray-50';
            textClass = 'text-gray-400';
            borderClass = 'border-gray-100 border-2';
        } else if (clubClosed) {
            bgClass = 'bg-red-50';
            textClass = 'text-red-700';
            borderClass = 'border-red-200 border-2';
        } else if (isHoliday) {
            bgClass = 'bg-red-100';
            textClass = 'text-red-700';
            borderClass = 'border-red-200 border-2 ';
        } else if (shortened) {
            bgClass = 'bg-yellow-50';
            textClass = 'text-yellow-700 border-2';
            borderClass = 'border-yellow-200 border-2';
        } else if (isToday) {
            bgClass = 'bg-blue-50';
            textClass = 'text-blue-700';
            borderClass = 'border-blue-300 border-2';
        } else if (isWeekend) {
            bgClass = 'bg-indigo-50';
            textClass = 'text-indigo-700';
            borderClass = 'border-indigo-100 border-2';
        }

        const opacityClass = (isPast && !isToday) ? 'opacity-80' : '';
        const cls = `cursor-pointer p-2 ${bgClass} ${textClass} ${borderClass} border-2 rounded-lg h-20 flex flex-col justify-between text-sm transition-all overflow-hidden ${opacityClass}`;

        const hoursText = `${Math.round(day.paid_completed_hours || 0)}/${Math.round(day.total_hours || 0)}`;

        return html`
            <div class="${cls}" data-date="${day.date}" data-weekend="${isWeekend}" data-club-closed="${clubClosed}">
                <!-- Верх: дата + бейджи статусов -->
                <div class="flex justify-between items-start gap-2">
                    <span class="text-sm font-medium">${date.getDate()}</span>

                    <div class="flex items-center gap-1 ml-auto">
                        ${isWeekend ? html`
                            <span class="text-[10px] px-1 py-0.5 rounded bg-white/60 border border-transparent ${isCurrentMonth ? 'text-indigo-700' : 'text-gray-400'}"
                                  title="Выходной недели">
              ${dayIndex === 5 ? 'СБ' : 'ВС'}
            </span>` : ''}

                        ${clubClosed ? html`
                            <span class="text-[10px] px-1 py-0.5 rounded bg-red-100 border border-red-200 text-red-700 font-medium"
                                  title="Клуб закрыт">
              Закрыт
            </span>` : ''}

                        ${isHoliday && !clubClosed ? html`
                            <span class="text-[10px] px-1 py-0.5 rounded bg-red-100 border border-red-200 text-red-700"
                                  title="Праздник">
              Праздник
            </span>` : ''}

                        ${shortened && !clubClosed ? html`
                            <span class="text-[10px] px-1 py-0.5 rounded bg-yellow-100 border border-yellow-200 text-yellow-700"
                                  title="Сокращённый день">
              Сокр.
            </span>` : ''}
                    </div>
                </div>

                <!-- Низ: одна строка — брони (круг) и часы для админа -->
                <div class="flex items-center justify-between gap-2">
                    ${bookings ? html`
                        <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold"
                              title="${bookings} брони">
            ${bookings}
          </span>` : html`<span class="w-6"></span>`}

                    ${isAdmin ? html`
                        <span class="min-w-0 text-[10px] truncate px-1 py-0.5 rounded bg-gray-50 border border-gray-200 text-gray-700"
                              title="${hoursText} часов (оплачено/всего)">
            ⏰ ${hoursText} ч
          </span>` : html`<span class="w-6"></span>`}
                </div>
            </div>
        `;
    }
};