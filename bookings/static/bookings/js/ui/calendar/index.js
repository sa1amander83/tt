import {DayView} from './day.js';
import {WeekView} from './week.js';
import {MonthView} from './month.js';
import {formatDate, getMonday, getWeekInterval} from '../../utils/date.js';
import {CalendarAPI} from "../../api/calendar.js";
import {BookingModal} from '../bookingModal/index.js';

const views = {day: DayView, week: WeekView, month: MonthView};

export const CalendarUI = {
    store: null,

    init(store) {
        this.store = store;
        store.subscribe(() => this.render());
        this.bindNav();
        this.bindFilters();
    },
    bindFilters() {
        $('#table-filter, #status-filter').on('change', () => {
            const tableFilter = $('#table-filter').val();
            const statusFilter = $('#status-filter').val();
            this.store.set({tableFilter, statusFilter});
        });
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
        const lastFetchedData = this.lastFetchedData;
        const titleEl = $('#calendar-title');
        const workingHoursEl = $('#calendar-working-hours');
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
                text = getWeekInterval(currentDate); // используем getWeekInterval
                break;
            case 'month':
                text = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
                break;
        }
        titleEl.text(text);

       if (currentView === 'day' && workingHoursEl.length && lastFetchedData?.working_hours) {
        workingHoursEl.text(
            `Время работы клуба: ${lastFetchedData.working_hours.open_time} – ${lastFetchedData.working_hours.close_time}`
        );
        workingHoursEl.show();
    } else if (workingHoursEl.length) {
        workingHoursEl.hide();
    }
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
        // Удаляем старые обработчики перед добавлением новых
        $('#day-view-container, #week-view-container, #month-view-container')
            .off('click', '[data-date][data-time][data-table]');

        // Добавляем новый обработчик с правильным делегированием
        $('#day-view-container, #week-view-container, #month-view-container')
            .on('click', '[data-date][data-time][data-table]', async (e) => {
                const target = $(e.target).closest('[data-date][data-time][data-table]')[0];
                if (!target) return;

                const date = target.dataset.date;
                const time = target.dataset.time;
                const tableId = target.dataset.table;
                const status = target.dataset.status;
                const bookingId = target.dataset.booking_id;
                const clickable = target.dataset.clickable === 'true';
                const {user} = this.store.get();

                // Разрешаем клик для свободных слотов или слотов с определенными статусами
                const allowedStatuses = ['available', 'expired', 'cancelled', 'returned'];

                if (allowedStatuses.includes(status) || (bookingId && user?.is_staff)) {
                    e.stopPropagation();

                    if (allowedStatuses.includes(status)) {
                        await BookingModal.open({date, time, tableId: Number(tableId)});
                    } else if (bookingId && user?.is_staff) {
                        import('../../api/booking.js').then(({BookingAPI}) => {
                            BookingAPI.get(bookingId).then(booking => {
                                this.showBookingDetails(booking);
                            }).catch(error => {
                                console.error('Failed to load booking details:', error);
                            });
                        });
                    }
                }
            });
    },
    showBookingDetails(booking) {
        // Создаем модальное окно с деталями брони
        const modal = html`
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 max-w-md w-full">
                    <h3 class="text-xl font-bold mb-4">Детали бронирования #${booking.id}</h3>
                    <div class="space-y-2">
                        <p><strong>Стол:</strong> ${booking.table.number}</p>
                        <p><strong>Дата:</strong> ${new Date(booking.start_time).toLocaleDateString()}</p>
                        <p><strong>Время:</strong> ${new Date(booking.start_time).toLocaleTimeString()} -
                            ${new Date(booking.end_time).toLocaleTimeString()}</p>
                        <p><strong>Статус:</strong> ${booking.status}</p>
                        <p><strong>Клиент:</strong> ${booking.user.name || booking.user.email}</p>
                        <p><strong>Сумма:</strong> ${booking.total_price} ₽</p>
                    </div>
                    <div class="mt-6 flex justify-end space-x-2">
                        <button class="px-4 py-2 bg-gray-300 rounded" onclick="this.closest('.fixed').remove()">
                            Закрыть
                        </button>
                        ${booking.status === 'pending' ?
                                `<button class="px-4 py-2 bg-red-500 text-white rounded" onclick="BookingAPI.cancel(${booking.id}).then(() => this.closest('.fixed').remove())">Отменить</button>` : ''}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async render() {
        const {currentDate, currentView, tableFilter, statusFilter} = this.store.get();
        if (!currentDate) return;

        /* 1. Показать нужный контейнер, скрыть остальные */
        $('#day-view-container, #week-view-container, #month-view-container')
            .addClass('hidden');
        $(`#${currentView}-view-container`).removeClass('hidden');


        const params = {
            date: formatDate(
                currentView === 'week' ? getMonday(currentDate) : currentDate
            ),
            view: currentView,
            table: tableFilter || 'all',
            status: statusFilter || 'all'
        };
        /* 4. Получить данные и отрисовать */
        const data = await CalendarAPI.data(params);
        $(`#${currentView}-view-container`)
            .html(views[currentView].render(data, this.store));

        /* 5. Подписки и обновление шапки */
        this.bindSlotClicks();
        this.lastFetchedData = data;
        this.updateHeader();
    }
};
window.CalendarUI = CalendarUI;