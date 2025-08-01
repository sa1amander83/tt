import { DayView }  from './day.js';
import { WeekView } from './week.js';
import { MonthView } from './month.js';
import { formatDate, getMonday } from '../../utils/date.js';
import {CalendarAPI} from "../../api/calendar.js";
const views = { day: DayView, week: WeekView, month: MonthView };

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
      this.store.set({ currentDate: new Date() });
    });

    $('.view-btn').each((_, btn) => {
      $(btn).on('click', () => this.switchView(btn.dataset.view));
    });
  },

  navigate(dir) {
    const { currentDate, currentView } = this.store.get();
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
        console.warn(`Unknown view: ${currentView}`);
        return;
    }

    this.store.set({ currentDate: newDate });
  },

  switchView(view) {
    this.store.set({ currentView: view });
  },



  bindSlotClicks() {
  $('.cursor-pointer[data-date][data-time][data-table]').on('click', (e) => {
    const target = e.currentTarget;
    const date = target.dataset.date;
    const time = target.dataset.time;
    const tableId = target.dataset.table;

    // Передай данные в модальное окно

    import('../bookingModal/index.js').then(module => {
      module.BookingModal.open({ date, time,     tableId: Number(tableId) });
    });
  });
},



  async render() {
    const { currentDate, currentView } = this.store.get();
    const container = $(`#${currentView}-view-container`);

    if (!container.length) return;

    const dateParam = currentView === 'week'
      ? getMonday(currentDate)
      : currentDate;

    const params = {
      date: formatDate(dateParam),
      view: currentView,
      table: $('#table-filter').val() || 'all',
      status: $('#status-filter').val() || 'all'
    };

    const data = await CalendarAPI.data(params);
    container.html(views[currentView].render(data, this.store));
    this.bindSlotClicks();
  }
};
