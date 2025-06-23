import { AppState } from './core/state';
import { BookingModal } from './ui/modal';
import { CalendarView } from './views/calendar';
import { initAuth } from './core/auth';

class TennisAp {
  constructor() {
    this.state = new AppState();
    this.modal = new BookingModal();
    this.calendar = new CalendarView(this.state);

    this.init();
  }

  async init() {
    try {
      await initAuth(this.state);
      await this.state.init();

      this.calendar.render();
      this.setupEventListeners();
    } catch (error) {
      console.error('App initialization failed:', error);
      showError('Application initialization failed');
    }
  }

         setupEventListeners() {
            // Навигация по календарю
            elements.prevBtn?.addEventListener('click', async () => {
                await navigate(-1); // Добавляем await
            });

            elements.nextBtn?.addEventListener('click', async () => {
                await navigate(1); // Добавляем await
            });


            elements.todayBtn?.addEventListener('click', async () => {
                goToToday();
                await loadSiteSettings(state.currentDate);
                renderCalendar();
            });
            // Переключение представлений
            elements.dayView?.addEventListener('click', () => switchView('day'));
            elements.weekView?.addEventListener('click', () => switchView('week'));
            elements.monthView?.addEventListener('click', () => switchView('month'));

            // Фильтры
            elements.tableFilter?.addEventListener('change', renderCalendar);
            elements.statusFilter?.addEventListener('change', renderCalendar);

            // Модальное окно
            elements.closeModalBtn?.addEventListener('click', closeModal);
            elements.cancelBookingBtn?.addEventListener('click', closeModal);
            elements.bookingForm?.addEventListener('submit', handleBookingSubmit);

            // Изменение параметров брони
            elements.duration?.addEventListener('change', updateBookingCost);
            elements.tableSelect?.addEventListener('change', updateBookingCost);
            elements.participants?.addEventListener('change', updateBookingCost);
            elements.equipmentCheckboxes?.forEach(checkbox => {
                checkbox.addEventListener('change', updateBookingCost);
            });

            // Обработка кликов по слотам
            elements.monthContainer?.addEventListener('click', async function (event) {
                const dayElement = event.target.closest('[data-date]');
                if (dayElement && dayElement.dataset.date) {
                    const selectedDate = new Date(dayElement.dataset.date);
                    state.currentDate = selectedDate;
                    state.currentView = 'day';
                    updateUI();

                    await loadSiteSettings(selectedDate); // обязательно await
                    renderCalendar();
                }
            });
            elements.weekContainer?.addEventListener('click', async function (event) {
                const slotElement = event.target.closest('[data-date][data-table]');
                if (slotElement) {
                    const selectedDate = new Date(slotElement.dataset.date);
                    const today = new Date();
                    const isPastDay = selectedDate < new Date(today.getFullYear(), today.getMonth(), today.getDate());

                    // Если пользователь не админ и день прошёл — игнорируем клик
                    if (isPastDay && !state.isAdmin) {
                        return;
                    }

                    state.currentDate = selectedDate;
                    state.currentView = 'day';
                    updateUI();

                    await loadSiteSettings(selectedDate);
                    renderCalendar();
                }
            });


            if (elements.dayContainer) {
                elements.dayContainer.addEventListener('click', function (event) {
                    const slot = event.target.closest('.booking-slot-available');
                    if (slot) {
                        handleSlotClick(event, slot);
                    }
                });
            }


        }


  async handleNavigation(direction) {
    const newDate = new Date(this.state.currentDate);
    // Логика навигации...
    await this.calendar.render();
  }

  goToToday() {
    this.state.update({ currentDate: new Date() });
    this.calendar.render();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new BilliardsApp();
});