document.addEventListener('DOMContentLoaded', function() {
    // Основные элементы
    const elements = {
        views: {
            day: document.getElementById('day-view'),
            week: document.getElementById('week-view'),
            month: document.getElementById('month-view')
        },
        containers: {
            day: document.getElementById('day-view-container'),
            week: document.getElementById('week-view-container'),
            month: document.getElementById('month-view-container')
        },
        navigation: {
            prev: document.getElementById('prev-btn'),
            next: document.getElementById('next-btn'),
            today: document.getElementById('today-btn'),
            title: document.getElementById('calendar-title')
        },
        modal: {
            element: document.getElementById('booking-modal'),
            open: document.getElementById('new-booking-btn'),
            close: document.getElementById('close-modal'),
            cancel: document.getElementById('cancel-booking'),
            form: document.getElementById('booking-modal')?.querySelector('form')
        },
        filters: {
            table: document.getElementById('table-filter'),
            status: document.getElementById('status-filter')
        }
    };

    // Состояние приложения
    const state = {
        currentDate: new Date(),
        currentView: 'day',
        tables: []
    };

    // Инициализация приложения
    function init() {
        setupEventListeners();
        setActiveView(state.currentView);
        updateCalendarTitle();
        loadInitialData();
    }

    // Настройка обработчиков событий
    function setupEventListeners() {
        // Переключение представлений
        Object.entries(elements.views).forEach(([view, element]) => {
            element?.addEventListener('click', () => setActiveView(view));
        });

        // Навигация по календарю
        elements.navigation.prev?.addEventListener('click', () => navigate(-1));
        elements.navigation.next?.addEventListener('click', () => navigate(1));
        elements.navigation.today?.addEventListener('click', goToToday);

        // Модальное окно
        elements.modal.open?.addEventListener('click', showModal);
        elements.modal.close?.addEventListener('click', hideModal);
        elements.modal.cancel?.addEventListener('click', hideModal);
        elements.modal.form?.addEventListener('submit', handleFormSubmit);

        // Фильтры
        elements.filters.table?.addEventListener('change', () => loadViewData());
        elements.filters.status?.addEventListener('change', () => loadViewData());

        // Делегирование событий для слотов бронирования
        document.addEventListener('click', function(e) {
            const slot = e.target.closest('.bg-green-100.cursor-pointer');
            if (slot) handleSlotClick(slot);
        });
    }

    // Установка активного представления
    function setActiveView(view) {
        // Проверка допустимости представления
        if (!['day', 'week', 'month'].includes(view)) return;

        // Обновление состояния
        state.currentView = view;

        // Обновление UI
        Object.entries(elements.views).forEach(([v, element]) => {
            if (element) {
                element.classList.toggle('bg-green-600', v === view);
                element.classList.toggle('text-white', v === view);
                element.classList.toggle('bg-white', v !== view);
                element.classList.toggle('text-gray-900', v !== view);
            }
        });

        Object.values(elements.containers).forEach(container => {
            container?.classList.add('hidden');
        });
        elements.containers[view]?.classList.remove('hidden');

        // Загрузка данных
        loadViewData();
        updateCalendarTitle();
    }

    // Навигация по календарю
    function navigate(direction) {
        const date = new Date(state.currentDate);

        switch (state.currentView) {
            case 'day':
                date.setDate(date.getDate() + direction);
                break;
            case 'week':
                date.setDate(date.getDate() + (7 * direction));
                break;
            case 'month':
                date.setMonth(date.getMonth() + direction);
                break;
        }

        state.currentDate = date;
        loadViewData();
        updateCalendarTitle();
    }

    // Переход на сегодняшнюю дату
    function goToToday() {
        state.currentDate = new Date();
        loadViewData();
        updateCalendarTitle();
    }

    // Обновление заголовка календаря
    function updateCalendarTitle() {
        const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
        const date = state.currentDate;

        if (!elements.navigation.title) return;

        if (state.currentView === 'day') {
            elements.navigation.title.textContent =
                `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
        } else if (state.currentView === 'week') {
            const startOfWeek = new Date(date);
            startOfWeek.setDate(date.getDate() - date.getDay() + 1);

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 6);

            elements.navigation.title.textContent =
                `${startOfWeek.getDate()} ${months[startOfWeek.getMonth()]} - ` +
                `${endOfWeek.getDate()} ${months[endOfWeek.getMonth()]} ${date.getFullYear()}`;
        } else if (state.currentView === 'month') {
            elements.navigation.title.textContent =
                `${months[date.getMonth()]} ${date.getFullYear()}`;
        }
    }

    // Загрузка данных представления
    function loadViewData() {
        const dateStr = state.currentDate.toISOString().split('T')[0];
        const tableFilter = elements.filters.table?.value || 'all';
        const statusFilter = elements.filters.status?.value || 'all';

        fetch(`/bookings/${state.currentView}/?date=${dateStr}&table=${tableFilter}&status=${statusFilter}`)
            .then(response => response.text())
            .then(html => {
                if (elements.containers[state.currentView]) {
                    elements.containers[state.currentView].innerHTML = html;
                }
            })
            .catch(error => console.error('Error loading view data:', error));
    }

    // Загрузка начальных данных
    function loadInitialData() {
        // Здесь можно загрузить дополнительные данные, если нужно
        loadUserBookings();
    }

    // Загрузка бронирований пользователя
    function loadUserBookings() {
        fetch('/bookings/user-bookings/')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('user-bookings-container');
                if (!container) return;

                if (data.bookings && data.bookings.length > 0) {
                    let html = `
                        <table class="min-w-full bg-white">
                            <thead>
                                <tr>
                                    <th class="py-2 px-4 border-b">Дата</th>
                                    <th class="py-2 px-4 border-b">Время</th>
                                    <th class="py-2 px-4 border-b">Стол</th>
                                    <th class="py-2 px-4 border-b">Статус</th>
                                    <th class="py-2 px-4 border-b">Действия</th>
                                </tr>
                            </thead>
                            <tbody>`;

                    data.bookings.forEach(booking => {
                        html += `
                            <tr>
                                <td class="py-2 px-4 border-b">${booking.date}</td>
                                <td class="py-2 px-4 border-b">${booking.start_time}-${booking.end_time}</td>
                                <td class="py-2 px-4 border-b">Стол #${booking.table}</td>
                                <td class="py-2 px-4 border-b">${booking.status}</td>
                                <td class="py-2 px-4 border-b">
                                    <button class="text-red-600 hover:text-red-800 mr-2">Отменить</button>
                                    <button class="text-blue-600 hover:text-blue-800">Оплатить</button>
                                </td>
                            </tr>`;
                    });

                    html += `</tbody></table>`;
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="text-center py-4 text-gray-500">У вас нет активных бронирований</div>';
                }
            })
            .catch(error => console.error('Error loading user bookings:', error));
    }

    // Обработка клика на свободный слот
    function handleSlotClick(slot) {
        const time = slot.getAttribute('data-time');
        const table = slot.getAttribute('data-table');

        if (time && table) {
            const today = new Date();
            const dateString = today.toISOString().split('T')[0];

            // Заполняем форму
            document.getElementById('booking-date')?.value = dateString;
            document.getElementById('booking-start-time')?.value = time;
            document.getElementById('booking-table')?.value = table;

            // Показываем модальное окно
            showModal();

            // Обновляем стоимость
            updateBookingCost();
        }
    }

    // Управление модальным окном
    function showModal() {
        elements.modal.element?.classList.remove('hidden');
    }

    function hideModal() {
        elements.modal.element?.classList.add('hidden');
    }

    // Обновление стоимости бронирования
    function updateBookingCost() {
        const duration = parseInt(document.getElementById('booking-duration')?.value || 1);
        const equipmentRental = document.getElementById('booking-equipment')?.checked ? 200 : 0;

        const tableSelect = document.getElementById('booking-table');
        const tableOption = tableSelect?.options[tableSelect.selectedIndex];
        const tableType = tableOption?.text.includes('Профессиональный') ? 'pro' : 'standard';

        const hourlyRate = tableType === 'pro' ? 500 : 400;
        const tableRental = hourlyRate * duration;
        const total = tableRental + equipmentRental;

        const costElements = {
            table: document.querySelector('.pt-4 .mb-2:nth-child(1) .font-medium:last-child'),
            equipment: document.querySelector('.pt-4 .mb-2:nth-child(2) .font-medium:last-child'),
            total: document.querySelector('.pt-4 .font-medium:last-child')
        };

        if (costElements.table) costElements.table.textContent = `${tableRental} ₽`;
        if (costElements.equipment) costElements.equipment.textContent = `${equipmentRental} ₽`;
        if (costElements.total) costElements.total.textContent = `${total} ₽`;
    }

    // Обработка отправки формы
    function handleFormSubmit(e) {
        e.preventDefault();

        const formData = new FormData(elements.modal.form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        fetch('/bookings/create/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                hideModal();
                loadViewData();
                loadUserBookings();
                alert('Бронирование успешно создано!');
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при отправке формы');
        });
    }

    // Запуск приложения
    init();
});