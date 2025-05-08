class CalendarManager {
    constructor() {
        this.currentDate = new Date();
        this.currentView = 'day';
        this.initElements();
        this.bindEvents();
        this.setActiveView('day');
        this.updateCalendarTitle();
    }

    initElements() {
        // Views
        this.dayView = document.getElementById('day-view');
        this.weekView = document.getElementById('week-view');
        this.monthView = document.getElementById('month-view');

        // Containers
        this.dayViewContainer = document.getElementById('day-view-container');
        this.weekViewContainer = document.getElementById('week-view-container');
        this.monthViewContainer = document.getElementById('month-view-container');

        // Navigation
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.todayBtn = document.getElementById('today-btn');
        this.calendarTitle = document.getElementById('calendar-title');

        // Modal
        this.newBookingBtn = document.getElementById('new-booking-btn');
        this.bookingModal = document.getElementById('booking-modal');
        this.closeModal = document.getElementById('close-modal');
        this.cancelBooking = document.getElementById('cancel-booking');
    }

    bindEvents() {
        // View switching
        this.dayView.addEventListener('click', () => this.setActiveView('day'));
        this.weekView.addEventListener('click', () => this.setActiveView('week'));
        this.monthView.addEventListener('click', () => this.setActiveView('month'));

        // Navigation
        this.prevBtn.addEventListener('click', () => this.navigate(-1));
        this.nextBtn.addEventListener('click', () => this.navigate(1));
        this.todayBtn.addEventListener('click', () => this.goToToday());

        // Modal
        if (this.newBookingBtn) {
            this.newBookingBtn.addEventListener('click', () => this.showModal());
        }
        if (this.closeModal) {
            this.closeModal.addEventListener('click', () => this.hideModal());
        }
        if (this.cancelBooking) {
            this.cancelBooking.addEventListener('click', () => this.hideModal());
        }

        // Date cells in month view
        document.querySelectorAll('#month-view-container .cursor-pointer').forEach(cell => {
            cell.addEventListener('click', () => this.handleDateCellClick(cell));
        });

        // Free slots in day view
        document.querySelectorAll('.bg-green-100.cursor-pointer').forEach(slot => {
            slot.addEventListener('click', () => this.handleSlotClick(slot));
        });
    }

    setActiveView(view) {
        // Reset buttons
        [this.dayView, this.weekView, this.monthView].forEach(btn => {
            btn.classList.remove('bg-green-600', 'text-white');
            btn.classList.add('bg-white', 'text-gray-900', 'border', 'border-gray-200');
        });

        // Hide containers
        [this.dayViewContainer, this.weekViewContainer, this.monthViewContainer].forEach(container => {
            container.classList.add('hidden');
        });

        // Activate selected view
        const activeButton = {
            'day': this.dayView,
            'week': this.weekView,
            'month': this.monthView
        }[view];

        const activeContainer = {
            'day': this.dayViewContainer,
            'week': this.weekViewContainer,
            'month': this.monthViewContainer
        }[view];

        if (activeButton && activeContainer) {
            activeButton.classList.remove('bg-white', 'text-gray-900', 'border', 'border-gray-200');
            activeButton.classList.add('bg-green-600', 'text-white');
            activeContainer.classList.remove('hidden');
            this.currentView = view;
            this.updateCalendarTitle();
        }
    }

    navigate(direction) {
        const actions = {
            'day': () => this.currentDate.setDate(this.currentDate.getDate() + direction),
            'week': () => this.currentDate.setDate(this.currentDate.getDate() + (7 * direction)),
            'month': () => this.currentDate.setMonth(this.currentDate.getMonth() + direction)
        };

        if (actions[this.currentView]) {
            actions[this.currentView]();
            this.updateCalendarTitle();
            // Здесь можно добавить загрузку данных для нового периода
        }
    }

    goToToday() {
        this.currentDate = new Date();
        this.updateCalendarTitle();
        // Здесь можно добавить загрузку данных для текущего периода
    }

    updateCalendarTitle() {
        const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

        let title = '';

        switch(this.currentView) {
            case 'day':
                title = `${this.currentDate.getDate()} ${months[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
                break;
            case 'week':
                const startOfWeek = new Date(this.currentDate);
                const dayOfWeek = this.currentDate.getDay() || 7;
                startOfWeek.setDate(this.currentDate.getDate() - dayOfWeek + 1);

                const endOfWeek = new Date(startOfWeek);
                endOfWeek.setDate(startOfWeek.getDate() + 6);

                title = `${startOfWeek.getDate()} ${months[startOfWeek.getMonth()]} - ${endOfWeek.getDate()} ${months[endOfWeek.getMonth()]} ${this.currentDate.getFullYear()}`;
                break;
            case 'month':
                title = `${months[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
                break;
        }

        this.calendarTitle.textContent = title;
    }

    showModal() {
        this.bookingModal.classList.remove('hidden');
    }

    hideModal() {
        this.bookingModal.classList.add('hidden');
    }

    handleDateCellClick(cell) {
        const day = parseInt(cell.querySelector('.font-medium').textContent);
        this.currentDate.setDate(day);
        this.setActiveView('day');
    }

    handleSlotClick(slot) {
        const time = slot.getAttribute('data-time');
        const table = slot.getAttribute('data-table');

        if (time && table) {
            const today = new Date();
            const dateString = today.toISOString().split('T')[0];
            document.getElementById('booking-date').value = dateString;
            document.getElementById('booking-start-time').value = time;
            document.getElementById('booking-table').value = table;
            this.showModal();
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const calendar = new CalendarManager();

    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
});