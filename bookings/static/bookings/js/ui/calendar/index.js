import {DayView} from './day.js';
import {WeekView} from './week.js';
import {MonthView} from './month.js';
import {formatDate, getMonday} from '../../utils/date.js';
import {CalendarAPI} from "../../api/calendar.js";

const views = {day: DayView, week: WeekView, month: MonthView};

export const CalendarUI = {
    store: null,

    init(store) {
        this.store = store;
        store.subscribe(() => this.render());
        this.bindNav();
    },

    bindNav() {
        $('#prev-btn').on('click', () => this.navigate(-1));
        $('#next-btn').on('click', () => this.navigate(1));
        $('#today-btn').on('click', () => {
            this.store.set({currentDate: new Date()});
        });

        $('.view-btn').each((_, btn) => {
            $(btn).on('click', () => this.switchView(btn.dataset.view));
        });
    },

    navigate(dir) {
        const {currentDate, currentView} = this.store.get();
        const newDate = new Date(currentDate);

        switch (currentView) {
            case 'day':
                newDate.setDate(newDate.getDate() + dir);
                break;
            case 'week':
                newDate.setDate(newDate.getDate() + 7 * dir);
                break;
            case 'month':
                newDate.setMonth(newDate.getMonth() + dir);
                break;
            default:
                showNotification(`Неизвестный представление: ${currentView}`, 'error');
                return;
        }

        this.store.set({currentDate: newDate});
    },

    showView(view) {
        // прячем все
        $('#day-view-container, #week-view-container, #month-view-container')
            .addClass('hidden');

        // показываем нужный
        $(`#${view}-view-container`).removeClass('hidden');
    },
    updateHeader() {
        const {currentDate, currentView} = this.store.get();
        const titleEl = $('#calendar-title');
        if (!titleEl.length) return;

        const months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ];
        const daysShort = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

        let text = '';
        switch (currentView) {
            case 'day':
                text = `${currentDate.getDate()} ${months[currentDate.getMonth()]} ${currentDate.getFullYear()} ${daysShort[currentDate.getDay()]}`;
                break;
            case 'week':
                const weekStart = getMonday(currentDate);
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekEnd.getDate() + 6);
                text = `${weekStart.getDate()}–${weekEnd.getDate()} ${months[weekEnd.getMonth()]} ${weekEnd.getFullYear()}`;
                break;
            case 'month':
                text = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
                break;
        }
        titleEl.text(text);
    },
    switchView(view) {
        this.store.set({currentView: view});

        // подсветка активной кнопки
        $('.view-btn').removeClass('bg-green-600 text-white')
            .addClass('bg-white text-gray-900 border');
        $(`[data-view="${view}"]`)
            .addClass('bg-green-600 text-white')
            .removeClass('bg-white text-gray-900 border');
    },


    bindSlotClicks() {
        $('.cursor-pointer[data-date][data-time][data-table]').on('click', (e) => {
            const target = e.currentTarget;
            const date = target.dataset.date;
            const time = target.dataset.time;
            const tableId = target.dataset.table;

            // Передай данные в модальное окно

            import('../bookingModal/index.js').then(module => {
                module.BookingModal.open({date, time, tableId: Number(tableId)});
            });
        });
    },


    async render() {
        const {currentDate, currentView} = this.store.get();

        /* 1. Показать нужный контейнер, скрыть остальные */
        $('#day-view-container, #week-view-container, #month-view-container')
            .addClass('hidden');
        $(`#${currentView}-view-container`).removeClass('hidden');

        /* 2. Определить дату для запроса */
        const dateParam = currentView === 'week'
            ? getMonday(currentDate)
            : currentDate;

        /* 3. Сформировать параметры API */
        const params = {
            date: formatDate(dateParam),
            view: currentView,
            table: $('#table-filter').val() || 'all',
            status: $('#status-filter').val() || 'all'
        };

        /* 4. Получить данные и отрисовать */
        const data = await CalendarAPI.data(params);
        $(`#${currentView}-view-container`)
            .html(views[currentView].render(data, this.store));

        /* 5. Подписки и обновление шапки */
        this.bindSlotClicks();
        this.updateHeader();
    }
};
