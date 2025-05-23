//функции бронирования
document.addEventListener('DOMContentLoaded', async function () {
    // Конфигурация API
    const API_ENDPOINTS = {
        RATES: '/bookings/api/rates/',
        TABLES: '/bookings/api/tables/',
        CALENDAR: '/bookings/api/calendar/',
        BOOKINGS: '/bookings/api/bookings/',
        CALCULATE: '/bookings/api/calculate/',

        USER_BOOKINGS: '/bookings/api/user-bookings/',
        SITE_SETTINGS: '/bookings/api/site-settings/'
    };

    // Состояние приложения
    const state = {
        currentDate: new Date(),
        currentView: 'day',
        rates: {},
        tables: [],
        bookings: [],
        pricingPlan: null,
        equipment: []
    };

    // Кэш элементов DOM
    const elements = {
        // Навигация
        prevBtn: document.getElementById('prev-btn'),
        nextBtn: document.getElementById('next-btn'),
        todayBtn: document.getElementById('today-btn'),
        calendarTitle: document.getElementById('calendar-title'),

        // Представления
        dayView: document.getElementById('day-view'),
        weekView: document.getElementById('week-view'),
        monthView: document.getElementById('month-view'),
        dayContainer: document.getElementById('day-view-container'),
        weekContainer: document.getElementById('week-view-container'),
        monthContainer: document.getElementById('month-view-container'),
        userBookingsContainer: document.getElementById('user-bookings-container'),
        // Фильтры
        tableFilter: document.getElementById('table-filter'),
        statusFilter: document.getElementById('status-filter'),

        // Модальное окно
        modal: document.getElementById('booking-modal'),
        closeModalBtn: document.getElementById('close-modal'),
        cancelBookingBtn: document.getElementById('cancel-booking'),
        bookingForm: document.getElementById('booking-form'),
        bookingDate: document.getElementById('booking-date'),
        startTime: document.getElementById('booking-start-time'),
        duration: document.getElementById('booking-duration'),
        tableSelect: document.getElementById('booking-table'),
        equipmentCheckboxes: document.querySelectorAll('.equipment-checkbox'),
        participants: document.getElementById('participants'),
        notes: document.getElementById('booking-notes'),
        costDisplay: {
            table: document.getElementById('table-cost'),
            equipment: document.getElementById('equipment-cost'),
            total: document.getElementById('total-cost')
        }
    };

    // Инициализация приложения
    async function init() {
        try {
            await loadInitialData();
            setupEventListeners();
            await renderCalendar();
            updateUI();
        } catch (error) {
            console.error('Ошибка инициализации:', error);
            showError('Не удалось загрузить данные приложения');
        }
    }

    // Загрузка начальных данных
    async function loadInitialData() {
        try {
            const [ratesRes, tablesRes, userBookingsRes, siteSettingsRes] = await Promise.all([
                fetch(API_ENDPOINTS.RATES),
                fetch(API_ENDPOINTS.TABLES),
                fetch(API_ENDPOINTS.USER_BOOKINGS),
                fetch(API_ENDPOINTS.SITE_SETTINGS),
            ]);

            if (!ratesRes.ok) throw new Error('Ошибка загрузки тарифов');
            if (!tablesRes.ok) throw new Error('Ошибка загрузки столов');
            if (!siteSettingsRes.ok) throw new Error('Ошибка загрузки настроек сайта');

            const settingsData = await siteSettingsRes.json();
            state.siteSettings = {
                opening_time: settingsData.opening_time?.open_time || "9:00",
                closing_time: settingsData.closing_time?.close_time || "22:00"
            };

            if (!/^\d{1,2}:\d{2}$/.test(state.siteSettings.opening_time)) {
                state.siteSettings.opening_time = "9:00";
            }

            if (!/^\d{1,2}:\d{2}$/.test(state.siteSettings.closing_time)) {
                state.siteSettings.closing_time = "22:00";
            }

            state.rates = await ratesRes.json();
            state.tables = await tablesRes.json();
            state.pricingPlan = state.rates.pricing_plan;

            if (userBookingsRes.ok) {
                const userBookingsData = await userBookingsRes.json();
                state.bookings = userBookingsData.bookings || [];
            }

        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            showError('Не удалось загрузить данные приложения');

            // fallback
            state.siteSettings = {
                opening_time: "9:00",
                closing_time: "22:00"
            };
        }

        initForm();
    }


    // Инициализация формы
    function initForm() {
        // Заполнение выбора столов
        if (elements.tableSelect && state.tables.length) {
            elements.tableSelect.innerHTML = state.tables.map(table =>
                `<option value="${table.id}" 
                    data-type="${table.type}" 
                    data-capacity="${table.capacity}">
                    Стол #${table.number} (${table.type})
                </option>`
            ).join('');
        }

        // Установка текущей даты
        if (elements.bookingDate) {
            elements.bookingDate.valueAsDate = new Date();
        }

        // Инициализация временных слотов
        initTimeSlots();

        // Первоначальный расчет стоимости
        updateBookingCost();
    }

    // Инициализация временных слотов
    function initTimeSlots() {
        if (!elements.startTime) return;

        elements.startTime.innerHTML = '';

        // Парсим время из формата "HH:MM"
        const parseTime = (timeStr, defaultHour) => {
            if (!timeStr) return defaultHour;
            const [hours, minutes] = timeStr.split(':').map(Number);
            return !isNaN(hours) ? hours : defaultHour;
        };

        let startHour = parseTime(state.siteSettings.opening_time, 9);
        let endHour = parseTime(state.siteSettings.closing_time, 22);

        // Проверяем, что время открытия раньше времени закрытия
        if (startHour >= endHour) {
            console.warn('Время открытия должно быть раньше времени закрытия. Используются значения по умолчанию.');
            startHour = 9;
            endHour = 22;
        }

        for (let hour = startHour; hour < endHour; hour++) {
            const option = document.createElement('option');
            option.value = hour;
            option.textContent = `${hour.toString().padStart(2, '0')}:00`;
            elements.startTime.appendChild(option);
        }
    }

    // Настройка обработчиков событий
    function setupEventListeners() {
        // Навигация по календарю
        elements.prevBtn?.addEventListener('click', () => navigate(-1));
        elements.nextBtn?.addEventListener('click', () => navigate(1));
        elements.todayBtn?.addEventListener('click', goToToday);

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
        document.addEventListener('click', handleSlotClick);
    }

    // Обработка кликов по слотам бронирования
    function handleSlotClick(event) {
        const slot = event.target.closest('.booking-slot-available');
        if (!slot) return;

        const date = slot.dataset.date;
        const time = slot.dataset.time;
        const tableId = slot.dataset.table;
        const slotId = slot.dataset.slotId;

        if (!date || !time || !tableId || !slotId) {
            console.error('Недостаточно данных для бронирования:', {date, time, tableId, slotId});
            return;
        }

        openBookingModal(date, time, tableId, slotId);
    }

    // Открытие модального окна бронирования
    function openBookingModal(date, time, tableId, slotId) {
        // Установка даты
        elements.bookingDate.value = date;

        // Установка времени
        const hour = time.split(':')[0];
        if (elements.startTime) {
            elements.startTime.value = hour;
        }

        // Установка стола
        elements.tableSelect.value = tableId;

        // Сохраняем ID слота в форме
        if (elements.bookingForm) {
            elements.bookingForm.dataset.slotId = slotId;
        }

        // Показать модальное окно
        elements.modal.classList.remove('hidden');

        // Обновить стоимость
        updateBookingCost();
    }

    // Закрытие модального окна
    function closeModal() {
        elements.modal.classList.add('hidden');
    }

    // Обновление стоимости бронирования
    async function updateBookingCost() {
        try {
            const tableId = elements.tableSelect?.value;
            if (!tableId) {
                resetCostDisplay();
                return;
            }

            const formData = {
                table_id: parseInt(tableId),
                duration: parseInt(elements.duration?.value) || 1,
                equipment: Array.from(elements.equipmentCheckboxes)
                    .filter(cb => cb.checked)
                    .map(cb => parseInt(cb.value)),
                participants: parseInt(elements.participants?.value) || 2
            };
            console.log('formData:', formData);
            const response = await fetch(API_ENDPOINTS.CALCULATE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Ошибка расчета стоимости');
            }

            const costData = await response.json();
            updateCostDisplay(costData);
        } catch (error) {
            console.error('Ошибка расчета стоимости:', error);
            showError(error.message);
        }
    }

    // Обновление отображения стоимости
    function updateCostDisplay(cost) {
        if (elements.costDisplay.table) {
            elements.costDisplay.table.textContent = `${cost.table_cost} ₽`;
        }
        if (elements.costDisplay.equipment) {
            elements.costDisplay.equipment.textContent = `${cost.equipment_cost} ₽`;
        }
        if (elements.costDisplay.total) {
            elements.costDisplay.total.textContent = `${cost.total_cost} ₽`;
        }
    }

    // Обработка отправки формы бронирования
    async function handleBookingSubmit(event) {
        event.preventDefault();

        try {
            const formData = {
                date: elements.bookingDate.value,
                start_time: elements.startTime.value,
                duration: elements.duration.value,
                table_id: elements.tableSelect.value,
                equipment: Array.from(elements.equipmentCheckboxes)
                    .filter(cb => cb.checked)
                    .map(cb => ({id: cb.value, quantity: 1})),
                participants: elements.participants.value,
                notes: elements.notes.value,
                slot_id: elements.bookingForm.dataset.slotId
            };

            const response = await fetch(API_ENDPOINTS.BOOKINGS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.message || 'Ошибка сервера');
            }

            const result = await response.json();

            if (result.success) {
                alert('Бронирование успешно создано!');
                closeModal();
                await renderCalendar();
                await loadUserBookings();
            } else {
                throw new Error(result.error || 'Неизвестная ошибка');
            }

        } catch (error) {
            console.error('Ошибка бронирования:', error);
            showError(error.message);
        }
    }

    // Загрузка бронирований пользователя
    async function loadUserBookings() {

        try {
            const response = await fetch(API_ENDPOINTS.USER_BOOKINGS);
            if (!response.ok) throw new Error('Ошибка загрузки бронирований');

            const data = await response.json();
            state.bookings = data.bookings || [];
            renderUserBookings();
        } catch (error) {
            console.error('Ошибка загрузки бронирований:', error);
        }
    }


    // Навигация по календарю
    function navigate(direction) {
        const newDate = new Date(state.currentDate);

        switch (state.currentView) {
            case 'day':
                newDate.setDate(newDate.getDate() + direction);
                break;
            case 'week':
                newDate.setDate(newDate.getDate() + (7 * direction));
                break;
            case 'month':
                newDate.setMonth(newDate.getMonth() + direction);
                // Корректировка даты, если вышли за пределы месяца
                const originalDate = newDate.getDate();
                newDate.setDate(1);
                newDate.setMonth(newDate.getMonth() + direction);
                const daysInMonth = new Date(newDate.getFullYear(), newDate.getMonth() + 1, 0).getDate();
                newDate.setDate(Math.min(originalDate, daysInMonth));
                break;
        }

        state.currentDate = newDate;
        updateUI();
        renderCalendar();
    }

    // Переход на сегодня
    function goToToday() {
        state.currentDate = new Date();
        renderCalendar();
        updateUI();
    }

    // Переключение представления
    function switchView(view) {
        if (['day', 'week', 'month'].includes(view)) {
            state.currentView = view;
            renderCalendar();
            updateUI();
        }
    }

    // Обновление интерфейса
    function updateUI() {
        updateCalendarTitle();
        updateActiveView();
        updateNavigationButtons();
    }

    function updateNavigationButtons() {
        if (elements.prevBtn && elements.nextBtn) {
            // Форматируем дату для передачи в атрибуты
            const dateStr = formatDateForAPI(state.currentDate);
            elements.prevBtn.dataset.date = dateStr;
            elements.nextBtn.dataset.date = dateStr;
        }
    }

    function formatDateForAPI(date) {
        return date.toISOString().split('T')[0]; // YYYY-MM-DD
    }

    // Обновление заголовка календаря
    function updateCalendarTitle() {
        const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
        const date = state.currentDate;

        let title = '';

        switch (state.currentView) {
            case 'day':
                title = `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
                break;
            case 'week': {
                const weekStart = new Date(date);
                weekStart.setDate(date.getDate() - weekStart.getDay());
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekStart.getDate() + 6);
                title = `${weekStart.getDate()}–${weekEnd.getDate()} ${months[weekEnd.getMonth()]} ${weekEnd.getFullYear()}`;
                break;
            }
            case 'month':
                title = `${months[date.getMonth()]} ${date.getFullYear()}`;
                break;
        }

        if (elements.calendarTitle) {
            elements.calendarTitle.textContent = title;
        }
    }

    // Обновление активного представления
    function updateActiveView() {
        if (elements.dayView) {
            elements.dayView.classList.toggle('bg-green-600', state.currentView === 'day');
            elements.dayView.classList.toggle('text-white', state.currentView === 'day');
        }
        if (elements.weekView) {
            elements.weekView.classList.toggle('bg-green-600', state.currentView === 'week');
            elements.weekView.classList.toggle('text-white', state.currentView === 'week');
        }
        if (elements.monthView) {
            elements.monthView.classList.toggle('bg-green-600', state.currentView === 'month');
            elements.monthView.classList.toggle('text-white', state.currentView === 'month');
        }

        if (elements.dayContainer) {
            elements.dayContainer.classList.toggle('hidden', state.currentView !== 'day');
        }
        if (elements.weekContainer) {
            elements.weekContainer.classList.toggle('hidden', state.currentView !== 'week');
        }
        if (elements.monthContainer) {
            elements.monthContainer.classList.toggle('hidden', state.currentView !== 'month');
        }
    }

    // Рендеринг календаря
    async function renderCalendar() {
        try {
            const dateStr = formatDateForAPI(state.currentDate);
            const params = new URLSearchParams({
                date: dateStr,
                view: state.currentView,
                table: elements.tableFilter?.value || 'all',
                status: elements.statusFilter?.value || 'all'
            });

            const response = await fetch(`${API_ENDPOINTS.CALENDAR}?${params}`);

            if (!response.ok) {
                throw new Error('Ошибка загрузки календаря');
            }

            const data = await response.json();
            renderView(data);
        } catch (error) {
            console.error('Ошибка рендеринга календаря:', error);
            showError('Не удалось загрузить данные календаря');
        }
    }


    // Рендеринг конкретного представления
    function renderView(data) {
        const container = elements[`${state.currentView}Container`];
        if (!container) return;

        switch (state.currentView) {
            case 'day':
                container.innerHTML = generateDayView(data);
                break;
            case 'week':
                const weekContainer = elements.weekContainer;
                const bookingContainer = elements.userBookingsContainer;

                weekContainer.innerHTML = renderWeekView(data);
                bookingContainer.innerHTML = renderUserBookings(data.user_bookings);

                document.querySelectorAll('.slot-available').forEach(cell => {
                    cell.addEventListener('click', () => {
                        const date = cell.dataset.date;
                        const tableId = cell.dataset.table;
                        alert(`Вы выбрали: ${date}, стол #${tableId}`);
                    });
                });
                break;
            case 'month':
                container.innerHTML = generateMonthView(data);
                break;
        }
    }

    // Генерация дневного представления
    function generateDayView(data) {
        if (!data.is_working_day) {
            return `
            <div class="p-8 text-center">
                <div class="inline-block p-6 bg-gray-100 rounded-lg">
                    <i class="fas fa-calendar-times text-4xl text-gray-400 mb-4"></i>
                    <h3 class="text-xl font-medium text-gray-700">Выходной день</h3>
                    <p class="text-gray-500 mt-2">${formatDate(data.date)}</p>
                </div>
            </div>
        `;
        }

        let slots = data.time_slots;
        if (slots.length === 0) {
            // Можно взять рабочие часы из data.working_hours и сгенерировать интервалы
            const open = data.working_hours.open; // например, "10:00"
            const close = data.working_hours.close; // например, "18:00"

            slots = generateDefaultTimeSlots(open, close, 60); // 60 минутный интервал
        }

        let html = `
    <div class="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
        <div class="flex border-b border-gray-200 bg-gray-50">
            <div class="w-24 md:w-32 flex-shrink-0 p-3">Время</div>
            ${data.tables.map(table => `
                <div class="flex-1 p-3 text-center font-medium">
                    Стол #${table.number}<br>
                    <span class="text-sm text-gray-500">${table.table_type}</span>
                </div>
            `).join('')}
        </div>
    `;

        slots.forEach(slotTime => {
            html += `
        <div class="flex border-b border-gray-200 last:border-b-0">
            <div class="w-24 md:w-32 flex-shrink-0 p-3 text-right text-sm text-gray-500">
                ${slotTime}
            </div>
            <div class="flex-1 grid grid-cols-${data.tables.length} divide-x divide-gray-200">
        `;

            data.tables.forEach(table => {
                const slotData = (data.day_schedule[table.id] && data.day_schedule[table.id][slotTime]) || null;
                const isAvailable = slotData ? slotData.status === 'available' : true;
                const bookingStatus = isAvailable ? 'Свободно' : (slotData ? slotData.status : 'Нет данных');

                html += `
            <div class="flex items-center justify-center p-2 min-h-12
                ${isAvailable ? 'bg-green-100 hover:bg-green-200 cursor-pointer' : 'bg-red-100 hover:bg-red-200'}"
                data-date="${data.date}"
                data-time="${slotTime}"
                data-table="${table.id}"
                data-slot-id="${slotData ? slotData.slot_id : ''}">
                <span class="text-sm ${isAvailable ? 'text-green-800' : 'text-red-800'}">
                    ${bookingStatus}
                </span>
            </div>
            `;
            });

            html += `</div></div>`;
        });

        html += '</div>';
        return html;
    }

    function formatDate(dateStr) {
        const date = new Date(dateStr);
        if (isNaN(date)) return dateStr; // если невалидная дата, вернуть как есть

        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();

        return `${day}.${month}.${year}`;
    }

// Пример функции генерации таймслотов по умолчанию
    function generateDefaultTimeSlots(openStr, closeStr, intervalMinutes) {
        const slots = [];
        const [openH, openM] = openStr.split(':').map(Number);
        const [closeH, closeM] = closeStr.split(':').map(Number);

        let current = new Date();
        current.setHours(openH, openM, 0, 0);

        const end = new Date();
        end.setHours(closeH, closeM, 0, 0);

        while (current < end) {
            let h = current.getHours().toString().padStart(2, '0');
            let m = current.getMinutes().toString().padStart(2, '0');
            slots.push(`${h}:${m}`);

            current = new Date(current.getTime() + intervalMinutes * 60000);
        }
        return slots;
    }


function renderWeekView(data) {
    if (!data.days || !data.tables) {
        return '<div class="p-4 text-center text-gray-500">Нет данных для отображения</div>';
    }

    // Заголовок с днями
    let html = `
    <div class="grid grid-cols-${data.days.length + 1} gap-px bg-gray-200 mb-2 text-sm font-medium">
        <div class="bg-white p-2"></div>
        ${data.days.map(day => {
            const date = new Date(day.date);
            return `
                <div class="bg-white p-2 text-center">
                    <div>${date.toLocaleDateString('ru-RU', { weekday: 'short' })}</div>
                    <div>${date.getDate()}</div>
                </div>`;
        }).join('')}
    </div>`;

    // Основная таблица
    html += `<div class="grid grid-cols-${data.days.length + 1} gap-px bg-gray-200 text-sm">`;

    // Левая колонка — столы
    html += `<div class="flex flex-col">`;
    data.tables.forEach(table => {
        html += `
            <div class="bg-white p-2 h-14 border-b flex flex-col justify-center">
                <div class="font-medium">Стол #${table.number}</div>
                <div class="text-xs text-gray-500">${table.table_type}</div>
            </div>`;
    });
    html += `</div>`;

    // Сетки по дням и столам
    html += data.days.map(day => {
        return `<div class="flex flex-col">` + data.tables.map(table => {
            const dayKey = day.date;
            const slots = data.week_schedule?.[table.id]?.[dayKey] || [];

            if (!day.is_working_day || !slots.length) {
                return `<div class="bg-gray-100 text-gray-400 h-14 border-b flex items-center justify-center">–</div>`;
            }

            const total = slots.length;
            const booked = slots.filter(slot => slot.status !== 'available').length;

            let cssClass = 'bg-green-100 text-green-800';
            if (booked === total) cssClass = 'bg-red-100 text-red-800';
            else if (booked > 0) cssClass = 'bg-yellow-100 text-yellow-800';

            return `<div class="h-14 border-b flex items-center justify-center ${cssClass} cursor-pointer"
                        title="Занято ${booked} из ${total}" 
                        data-date="${dayKey}" 
                        data-table="${table.id}">
                        ${booked}/${total}
                    </div>`;
        }).join('') + `</div>`;
    }).join('');

    html += `</div>`;
    return html;
}

    function renderUserBookings(bookings) {
        if (!bookings || bookings.length === 0) {
            return `<div class="text-gray-400">Нет активных бронирований на этой неделе.</div>`;
        }

        return `
    <table class="min-w-full border text-sm text-left">
        <thead>
            <tr class="bg-gray-100">
                <th class="px-3 py-2 border">Дата</th>
                <th class="px-3 py-2 border">Время</th>
                <th class="px-3 py-2 border">Стол</th>
                <th class="px-3 py-2 border">Статус</th>
            </tr>
        </thead>
        <tbody>
            ${bookings.map(booking => `
                <tr>
                    <td class="px-3 py-2 border">${new Date(booking.date).toLocaleDateString('ru-RU')}</td>
                    <td class="px-3 py-2 border">${booking.start}–${booking.end}</td>
                    <td class="px-3 py-2 border">#${booking.table_number}</td>
                    <td class="px-3 py-2 border">${booking.status}</td>
                </tr>
            `).join('')}
        </tbody>
    </table>`;
    }

    // Вставляем сгенерированную таблицу в контейнер
    // Генерация месячного представления
    function generateMonthView(data) {
        if (!data.weeks?.length || !data.tables?.length || !data.weeks[0]?.length) {
            return '<div class="p-4 text-center text-gray-500">Нет данных для отображения</div>';
        }

        let html = `
        <div class="overflow-x-auto">
            <table class="min-w-full border-collapse">
                <thead>
                    <tr>
                        <th class="p-2 border-b">Стол / Неделя</th>
                        ${data.weeks[0].map(dayStr => {
            const day = new Date(dayStr);
            return `<th class="p-2 border-b text-center">${day.getDate()}</th>`;
        }).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

        data.tables.forEach(table => {
            html += `
            <tr>
                <td class="p-2 border-b">
                    Стол #${table.number}<br>
                    <span class="text-xs text-gray-500">${table.type}</span>
                </td>
        `;

            data.weeks[0].forEach(dayStr => {
                const day = new Date(dayStr);
                const key = `${table.id}-${day.toISOString().split('T')[0]}`;
                const booking = data.month_schedule[key];

                html += `<td class="p-2 border-b">`;

                if (booking) {
                    html += `
                    <div class="mb-1 p-1 text-sm rounded 
                        ${booking.status === 'available' ? 'bg-green-100' : 'bg-red-100'}">
                        ${booking.start_time}-${booking.end_time}
                    </div>
                `;
                } else {
                    html += '<div class="text-sm text-gray-400">-</div>';
                }

                html += `</td>`;
            });

            html += `</tr>`;
        });

        html += `
                </tbody>
            </table>
        </div>
    `;

        return html;
    }

    // Получение CSRF токена
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // Показать ошибку
    function showError(message) {
        alert(`Ошибка: ${message}`);
    }

    // Запуск приложения
    init();
});


// document.addEventListener('DOMContentLoaded', function() {
//     // Основные элементы
//     const elements = {
//         views: {
//             day: document.getElementById('day-view'),
//             week: document.getElementById('week-view'),
//             month: document.getElementById('month-view')
//         },
//         containers: {
//             day: document.getElementById('day-view-container'),
//             week: document.getElementById('week-view-container'),
//             month: document.getElementById('month-view-container')
//         },
//         navigation: {
//             prev: document.getElementById('prev-btn'),
//             next: document.getElementById('next-btn'),
//             today: document.getElementById('today-btn'),
//             title: document.getElementById('calendar-title')
//         },
//         modal: {
//             element: document.getElementById('booking-modal'),
//             open: document.getElementById('new-booking-btn'),
//             close: document.getElementById('close-modal'),
//             cancel: document.getElementById('cancel-booking'),
//             form: document.getElementById('booking-modal')?.querySelector('form')
//         },
//         filters: {
//             table: document.getElementById('table-filter'),
//             status: document.getElementById('status-filter')
//         }
//     };
//
//     // Состояние приложения
//     const state = {
//         currentDate: new Date(),
//         currentView: 'day',
//         tables: []
//     };
//
//     // Инициализация приложения
//     function init() {
//         setupEventListeners();
//         setActiveView(state.currentView);
//         updateCalendarTitle();
//         loadInitialData();
//     }
//
//     // Настройка обработчиков событий
//     function setupEventListeners() {
//         // Переключение представлений
//         Object.entries(elements.views).forEach(([view, element]) => {
//             element?.addEventListener('click', () => setActiveView(view));
//         });
//
//         // Навигация по календарю
//         elements.navigation.prev?.addEventListener('click', () => navigate(-1));
//         elements.navigation.next?.addEventListener('click', () => navigate(1));
//         elements.navigation.today?.addEventListener('click', goToToday);
//
//         // Модальное окно
//         elements.modal.open?.addEventListener('click', showModal);
//         elements.modal.close?.addEventListener('click', hideModal);
//         elements.modal.cancel?.addEventListener('click', hideModal);
//         elements.modal.form?.addEventListener('submit', handleFormSubmit);
//
//         // Фильтры
//         elements.filters.table?.addEventListener('change', () => loadViewData());
//         elements.filters.status?.addEventListener('change', () => loadViewData());
//
//         // Делегирование событий для слотов бронирования
//         document.addEventListener('click', function(e) {
//             const slot = e.target.closest('.bg-green-100.cursor-pointer');
//             if (slot) handleSlotClick(slot);
//         });
//     }
//
//     // Установка активного представления
//     function setActiveView(view) {
//         // Проверка допустимости представления
//         if (!['day', 'week', 'month'].includes(view)) return;
//
//         // Обновление состояния
//         state.currentView = view;
//
//         // Обновление UI
//         Object.entries(elements.views).forEach(([v, element]) => {
//             if (element) {
//                 element.classList.toggle('bg-green-600', v === view);
//                 element.classList.toggle('text-white', v === view);
//                 element.classList.toggle('bg-white', v !== view);
//                 element.classList.toggle('text-gray-900', v !== view);
//             }
//         });
//
//         Object.values(elements.containers).forEach(container => {
//             container?.classList.add('hidden');
//         });
//         elements.containers[view]?.classList.remove('hidden');
//
//         // Загрузка данных
//         loadViewData();
//         updateCalendarTitle();
//     }
//
//     // Навигация по календарю
//     function navigate(direction) {
//         const date = new Date(state.currentDate);
//
//         switch (state.currentView) {
//             case 'day':
//                 date.setDate(date.getDate() + direction);
//                 break;
//             case 'week':
//                 date.setDate(date.getDate() + (7 * direction));
//                 break;
//             case 'month':
//                 date.setMonth(date.getMonth() + direction);
//                 break;
//         }
//
//         state.currentDate = date;
//         loadViewData();
//         updateCalendarTitle();
//     }
//
//     // Переход на сегодняшнюю дату
//     function goToToday() {
//         state.currentDate = new Date();
//         loadViewData();
//         updateCalendarTitle();
//     }
//
//     // Обновление заголовка календаря
//     function updateCalendarTitle() {
//         const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
//                        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
//         const date = state.currentDate;
//
//         if (!elements.navigation.title) return;
//
//         if (state.currentView === 'day') {
//             elements.navigation.title.textContent =
//                 `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
//         } else if (state.currentView === 'week') {
//             const startOfWeek = new Date(date);
//             startOfWeek.setDate(date.getDate() - date.getDay() + 1);
//
//             const endOfWeek = new Date(startOfWeek);
//             endOfWeek.setDate(startOfWeek.getDate() + 6);
//
//             elements.navigation.title.textContent =
//                 `${startOfWeek.getDate()} ${months[startOfWeek.getMonth()]} - ` +
//                 `${endOfWeek.getDate()} ${months[endOfWeek.getMonth()]} ${date.getFullYear()}`;
//         } else if (state.currentView === 'month') {
//             elements.navigation.title.textContent =
//                 `${months[date.getMonth()]} ${date.getFullYear()}`;
//         }
//     }
//
//     // Загрузка данных представления
//     function loadViewData() {
//         const dateStr = state.currentDate.toISOString().split('T')[0];
//         const tableFilter = elements.filters.table?.value || 'all';
//         const statusFilter = elements.filters.status?.value || 'all';
//
//         fetch(`/bookings/${state.currentView}/?date=${dateStr}&table=${tableFilter}&status=${statusFilter}`)
//             .then(response => response.text())
//             .then(html => {
//                 if (elements.containers[state.currentView]) {
//                     elements.containers[state.currentView].innerHTML = html;
//                 }
//             })
//             .catch(error => console.error('Error loading view data:', error));
//     }
//
//     // Загрузка начальных данных
//     function loadInitialData() {
//         // Здесь можно загрузить дополнительные данные, если нужно
//         loadUserBookings();
//     }
//
//     // Загрузка бронирований пользователя
//     function loadUserBookings() {
//         fetch('/bookings/user-bookings/')
//             .then(response => response.json())
//             .then(data => {
//                 const container = document.getElementById('user-bookings-container');
//                 if (!container) return;
//
//                 if (data.bookings && data.bookings.length > 0) {
//                     let html = `
//                         <table class="min-w-full bg-white">
//                             <thead>
//                                 <tr>
//                                     <th class="py-2 px-4 border-b">Дата</th>
//                                     <th class="py-2 px-4 border-b">Время</th>
//                                     <th class="py-2 px-4 border-b">Стол</th>
//                                     <th class="py-2 px-4 border-b">Статус</th>
//                                     <th class="py-2 px-4 border-b">Действия</th>
//                                 </tr>
//                             </thead>
//                             <tbody>`;
//
//                     data.bookings.forEach(booking => {
//                         html += `
//                             <tr>
//                                 <td class="py-2 px-4 border-b">${booking.date}</td>
//                                 <td class="py-2 px-4 border-b">${booking.start_time}-${booking.end_time}</td>
//                                 <td class="py-2 px-4 border-b">Стол #${booking.table}</td>
//                                 <td class="py-2 px-4 border-b">${booking.status}</td>
//                                 <td class="py-2 px-4 border-b">
//                                     <button class="text-red-600 hover:text-red-800 mr-2">Отменить</button>
//                                     <button class="text-blue-600 hover:text-blue-800">Оплатить</button>
//                                 </td>
//                             </tr>`;
//                     });
//
//                     html += `</tbody></table>`;
//                     container.innerHTML = html;
//                 } else {
//                     container.innerHTML = '<div class="text-center py-4 text-gray-500">У вас нет активных бронирований</div>';
//                 }
//             })
//             .catch(error => console.error('Error loading user bookings:', error));
//     }
//
//     // Обработка клика на свободный слот
//     function handleSlotClick(slot) {
//         const time = slot.getAttribute('data-time');
//         const table = slot.getAttribute('data-table');
//
//         if (time && table) {
//             const today = new Date();
//             const dateString = today.toISOString().split('T')[0];
//
//             /** Заполняем форму
//             document.getElementById('booking-date')?.value = dateString;
//             document.getElementById('booking-start-time')?.value = time;
//             document.getElementById('booking-table')?.value = table;
//             **/
//             // Показываем модальное окно
//             showModal();
//
//             // Обновляем стоимость
//             updateBookingCost();
//         }
//     }
//
//     // Управление модальным окном
//     function showModal() {
//         elements.modal.element?.classList.remove('hidden');
//     }
//
//     function hideModal() {
//         elements.modal.element?.classList.add('hidden');
//     }
//
//     // Обновление стоимости бронирования
//     function updateBookingCost() {
//         const duration = parseInt(document.getElementById('booking-duration')?.value || 1);
//         const equipmentRental = document.getElementById('booking-equipment')?.checked ? 200 : 0;
//
//         const tableSelect = document.getElementById('booking-table');
//         const tableOption = tableSelect?.options[tableSelect.selectedIndex];
//         const tableType = tableOption?.text.includes('Профессиональный') ? 'pro' : 'standard';
//
//         const hourlyRate = tableType === 'pro' ? 500 : 400;
//         const tableRental = hourlyRate * duration;
//         const total = tableRental + equipmentRental;
//
//         const costElements = {
//             table: document.querySelector('.pt-4 .mb-2:nth-child(1) .font-medium:last-child'),
//             equipment: document.querySelector('.pt-4 .mb-2:nth-child(2) .font-medium:last-child'),
//             total: document.querySelector('.pt-4 .font-medium:last-child')
//         };
//
//         if (costElements.table) costElements.table.textContent = `${tableRental} ₽`;
//         if (costElements.equipment) costElements.equipment.textContent = `${equipmentRental} ₽`;
//         if (costElements.total) costElements.total.textContent = `${total} ₽`;
//     }
//
//     // Обработка отправки формы
//     function handleFormSubmit(e) {
//         e.preventDefault();
//
//         const formData = new FormData(elements.modal.form);
//         const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
//
//         fetch('/bookings/create/', {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': csrfToken
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 hideModal();
//                 loadViewData();
//                 loadUserBookings();
//                 alert('Бронирование успешно создано!');
//             } else {
//                 alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('Произошла ошибка при отправке формы');
//         });
//     }
//
//     // Запуск приложения
//     init();
// });