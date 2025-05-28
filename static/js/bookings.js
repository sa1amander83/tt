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
        const isAdmin = document.getElementById('user_role').innerText === 'True';
        // Состояние приложения
        const state = {
            currentDate: new Date(),
            currentView: 'day',
            rates: {},
            tables: [],
            bookings: [],
            pricingPlan: null,
            equipment: [],
            isAdmin: isAdmin
        }

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
                table: document.getElementById('tariff-table-cost'),
                equipment: document.getElementById('tariff-equipment-cost'),
                total: document.getElementById('tariff-total-cost')
            }
        };

        // Инициализация приложения
        async function init() {
            try {
                await loadInitialData();
                await loadSiteSettings(state.currentDate);

                setupEventListeners();
                setupEquipmentHandlers(); // Добавляем эту строку

                if (!state.siteSettings.close_time || !state.siteSettings.close_time.match(/^\d{1,2}:\d{2}$/)) {
                    state.siteSettings.close_time = "22:00";
                }

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
                showLoader()
                const [ratesRes, tablesRes, userBookingsRes] = await Promise.all([fetch(API_ENDPOINTS.RATES), fetch(API_ENDPOINTS.TABLES), fetch(API_ENDPOINTS.USER_BOOKINGS)]);

                if (!ratesRes.ok) throw new Error('Ошибка загрузки тарифов');
                if (!tablesRes.ok) throw new Error('Ошибка загрузки столов');

                state.rates = await ratesRes.json();
                state.tables = await tablesRes.json();
                state.pricingPlan = state.rates.pricing_plan;

                // Загружаем настройки для текущей даты
                await loadSiteSettings(state.currentDate);

                if (userBookingsRes.ok) {
                    const userBookingsData = await userBookingsRes.json();
                    state.bookings = userBookingsData.bookings || [];
                }

            } catch (error) {
                console.error('Ошибка загрузки данных:', error);
                showError('Не удалось загрузить данные приложения');
            }
            hideLoader()
            initForm();
        }

        // Инициализация формы
        function initForm() {
            // Заполнение выбора столов
            if (elements.tableSelect && state.tables.length) {
                elements.tableSelect.innerHTML = state.tables.map(table => `<option value="${table.id}" 
                    data-type="${table.table_type}" 
                    data-capacity="${table.capacity}">
                    Стол #${table.number} (${table.table_type})
                </option>`).join('');
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

        elements.bookingDate?.addEventListener('change', async () => {
            const selectedDate = elements.bookingDate.valueAsDate;
            if (selectedDate) {
                state.currentDate = selectedDate;
                updateUI();
                await loadSiteSettings(selectedDate);
                await renderCalendar();
            }
        });

        async function loadSiteSettings(date) {
            try {
                const dateStr = date.toISOString().split('T')[0];
                showLoader()
                const response = await fetch(`${API_ENDPOINTS.SITE_SETTINGS}?date=${dateStr}`);

                if (!response.ok) throw new Error('Ошибка получения настроек');
                const data = await response.json();

                state.siteSettings = {
                    open_time: data.current_day.open_time || "09:00",
                    close_time: data.current_day.close_time || "22:00",
                    is_open: data.current_day.is_open !== false // по умолчанию true
                };

                initTimeSlots();
                hideLoader()
                return true;

            } catch (error) {
                console.error('Ошибка загрузки настроек дня:', error);
                state.siteSettings = {
                    open_time: "09:00", close_time: "22:00", is_open: true
                };
                initTimeSlots();
                return false;
            }
        }

        // Инициализация временных слотов
        function initTimeSlots() {
            if (!elements.startTime) return;

            elements.startTime.innerHTML = '';

            // Получаем время открытия и закрытия
            const [openHour, openMinute] = state.siteSettings.open_time.split(':').map(Number);
            const [closeHour, closeMinute] = state.siteSettings.close_time.split(':').map(Number);

            // Создаем Date объекты для удобства расчетов
            const openTime = new Date();
            openTime.setHours(openHour, openMinute, 0, 0);

            const closeTime = new Date();
            closeTime.setHours(closeHour, closeMinute, 0, 0);

            // Добавляем слоты с шагом 60 минут
            let currentTime = new Date(openTime);

            // Уменьшаем closeTime на 1 час, чтобы последний слот заканчивался в closeTime
            const lastSlotTime = new Date(closeTime);
            lastSlotTime.setHours(closeTime.getHours() - 1);

            const now = new Date();

            while (currentTime <= lastSlotTime) {
                // Пропускаем прошедшее время
                if (currentTime > now) {
                    const hours = currentTime.getHours().toString().padStart(2, '0');
                    const minutes = currentTime.getMinutes().toString().padStart(2, '0');
                    const timeString = `${hours}:${minutes}`;

                    const option = document.createElement('option');
                    option.value = timeString;
                    option.textContent = timeString;
                    elements.startTime.appendChild(option);
                }

                // Увеличиваем время на 1 час для следующего слота
                currentTime.setHours(currentTime.getHours() + 1);
            }
        }

        // Настройка обработчиков событий
        function setupEventListeners() {
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
                    if (isPastDay && !state.IsAdmin) {
                        return;
                    }

                    state.currentDate = selectedDate;
                    state.currentView = 'day';
                    updateUI();

                    await loadSiteSettings(selectedDate);
                    renderCalendar();
                }
            });
            elements.dayContainer?.addEventListener('click', function (event) {
                const slot = event.target.closest('.booking-slot-available');
                if (slot) {
                    handleSlotClick(event, slot);
                }
            });

        }

        // Обработка кликов по слотам бронирования
        function handleSlotClick(event, slot) {
            event.preventDefault();

            const date = slot.dataset.date;
            const time = slot.dataset.time;
            const tableId = slot.dataset.table;
            const slotId = slot.dataset.slotId || '';

            // Проверка доступности времени (если нужно)
            const now = new Date();
            const slotDateTime = new Date(`${date}T${time}`);

            if (slotDateTime < now) {
                showNotification('Это время уже прошло, выберите другое', 'error');
                return;
            }

            // Открываем модальное окно
            openBookingModal(date, time, tableId, slotId);
        }

        function setupEquipmentHandlers() {
            document.querySelectorAll('.equipment-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', function () {
                    const quantityEl = document.querySelector(`select[name="equipment_quantity_${this.value}"]`);
                    if (quantityEl) {
                        quantityEl.classList.toggle('hidden', !this.checked);
                    }
                    updateBookingCost();
                });
            });

            document.querySelectorAll('.equipment-quantity').forEach(select => {
                select.addEventListener('change', updateBookingCost);
            });
        }

        function updateTariffSummary(tariffName, tableCost, equipmentCost, totalCost) {
            const summaryBlock = document.getElementById('tariff-summary');
            const nameEl = document.getElementById('tariff-name');
            const tableCostEl = document.getElementById('tariff-table-cost');
            const equipmentCostEl = document.getElementById('tariff-equipment-cost');
            const totalCostEl = document.getElementById('tariff-total-cost');

            nameEl.textContent = tariffName || '—';
            tableCostEl.textContent = `${tableCost} ₽`;
            equipmentCostEl.textContent = `${equipmentCost} ₽`;
            totalCostEl.textContent = `${totalCost} ₽`;

            summaryBlock.classList.remove('hidden');
        }

        function isPastTime(dateStr, timeStr) {
            if (state.isAdmin) return false;
            const now = new Date();
            const [hours, minutes] = timeStr.split(':').map(Number);
            const slotDate = new Date(dateStr);
            slotDate.setHours(hours, minutes, 0, 0);
            return slotDate < now;
        }

        const formElement = elements.bookingForm;

        formElement.addEventListener('input', handleFormChange);
        formElement.addEventListener('change', handleFormChange);

        async function handleFormChange() {
            const date = elements.bookingDate.value;
            const time = elements.startTime.value;
            const tableId = document.getElementById('booking-table')?.value;
            const duration = parseInt(elements.duration?.value) || 60;

            if (!date || !time || !tableId || !duration) return;

            await fetchBookingInfoAndRecalculate({date, time, tableId, duration});
        }

        async function fetchBookingInfoAndRecalculate({date, time, tableId, duration}) {
            try {
                const response = await fetch(`/bookings/api/get-booking-info/?date=${date}&time=${time}&table_id=${tableId}&duration=${duration}`);
                const data = await response.json();

                if (!response.ok || data.error) {
                    alert(data.error || "Ошибка при получении тарифа.");
                    return;
                }

                const pricePerHour = data.price_per_hour;
                const pricePerHalfHour = data.price_per_half_hour;
                const tariffName = data.tariff_description || "Стандартный тариф";

                // Обновим dataset формы
                elements.bookingForm.dataset.pricePerHour = pricePerHour;
                elements.bookingForm.dataset.pricePerHalfHour = pricePerHalfHour;

                updateBookingCost({
                    tablePriceHour: pricePerHour,
                    tablePriceHalfHour: pricePerHalfHour,
                    equipment: data.equipment || [],
                    tariffName: tariffName
                });

            } catch (error) {
                console.error("Ошибка при получении тарифа:", error);
                showNotification("Ошибка при получении тарифа: " + error.message, 'error');
            }
        }


        // Открытие модального окна бронирования
        async function openBookingModal(date, time, tableId, slotId) {
            const formattedTime = time.includes(':') ? time : `${time}:00`;

            try {
                const response = await fetch(`/bookings/api/get-booking-info/?date=${date}&time=${formattedTime}&table_id=${tableId}`);
                const data = await response.json();

                if (!response.ok || data.error) {
                    alert(data.error || "Ошибка при получении тарифной информации.");
                    return;
                }

                // Установка базовых значений
                const {open_time, close_time} = state.siteSettings;
                const clubOpenTime = new Date(`${date}T${open_time}:00`);
                const clubCloseTime = new Date(`${date}T${close_time}:00`);
                const bookingStartTime = new Date(`${date}T${formattedTime}:00`);
                const maxDurationMinutes = Math.min(data.max_duration, Math.floor((clubCloseTime - bookingStartTime) / 60000));

                // Обновление UI
                updateTariffSummary(
                    data.tariff_description || "Стандартный тариф",
                    Math.round(data.price_per_half_hour),
                    0,
                    Math.round(data.final_price)
                );
                elements.bookingForm.dataset.pricePerHour = data.price_per_hour;
                elements.bookingForm.dataset.pricePerHalfHour = data.price_per_half_hour;

                elements.bookingDate.value = date;
                elements.startTime.value = formattedTime;

                populateTimeOptions(clubOpenTime, clubCloseTime, formattedTime);
                populateTableOptions(data.tables, tableId);
                populateParticipants(data.tables, tableId);
                populateDurationOptions(data.min_duration, maxDurationMinutes, data.max_duration);
                populateEquipmentOptions(data.equipment);

                // Сброс значений
                elements.participants.value = '2';
                elements.notes.value = '';
                document.getElementById('is-group').checked = false;

                if (elements.bookingForm) {
                    elements.bookingForm.dataset.slotId = slotId || '';
                }

                updateCostDisplay({
                    table_cost: data.base_price,
                    equipment_cost: 0,
                    total_cost: data.final_price
                });

                elements.modal.classList.remove('hidden');

            } catch (error) {
                console.error("Ошибка при открытии модалки бронирования:", error);
                alert("Не удалось получить информацию о бронировании. Повторите попытку позже.");
            }
        }

        function populateTimeOptions(startTime, endTime, selectedTime) {
            const select = document.getElementById('booking-start-time');
            select.innerHTML = '';

            let currentTime = new Date(startTime);
            while (currentTime <= endTime) {
                const timeStr = currentTime.toTimeString().slice(0, 5);
                const option = new Option(timeStr, timeStr);
                select.add(option);
                currentTime.setMinutes(currentTime.getMinutes() + 30);
            }

            if ([...select.options].some(opt => opt.value === selectedTime)) {
                select.value = selectedTime;
            } else {
                select.selectedIndex = 0;
            }
        }

        function populateTableOptions(tables, selectedId) {
            const select = document.getElementById('booking-table');
            if (!select) return;

            select.innerHTML = '';
            tables.forEach(table => {
                const option = new Option(`Стол #${table.number} (${table.table_type})`, table.id);
                option.dataset.maxPlayers = table.default_capacity || 2;
                select.add(option);
            });
            select.value = selectedId;

            const selectedTable = tables.find(t => t.id === parseInt(selectedId));
            const tableTypeElement = document.getElementById('table-type-name');
            if (tableTypeElement) {
                tableTypeElement.textContent = selectedTable?.table_type || '';
            }
        }

        function populateParticipants(tables, tableId) {
            const select = document.getElementById('participants');
            if (!select) return;

            const table = tables.find(t => t.id === parseInt(tableId));
            const maxPlayers = table?.default_capacity || 2;

            select.innerHTML = '';
            for (let i = 2; i <= maxPlayers; i++) {
                const option = new Option(`${i} игрок${i > 1 ? 'а' : ''}`, i);
                select.add(option);
            }
        }

        function populateDurationOptions(min, max, limit) {
            const select = document.getElementById('booking-duration');
            const step = 30;
            select.innerHTML = '';

            for (let dur = min; dur <= max; dur += step) {
                const hours = Math.floor(dur / 60);
                const minutes = dur % 60;
                let label = hours > 0 ? `${hours} час${hours >= 5 ? 'ов' : hours > 1 ? 'а' : ''}` : '';
                if (minutes > 0) label += ` ${minutes} мин`;

                const option = new Option(label.trim() + (dur === max && max < limit ? ' (до закрытия)' : ''), dur);
                select.add(option);
            }

            select.value = 60;
            elements.duration.addEventListener('change', () => {
                updateBookingCost();
            });
        }

        function populateEquipmentOptions(equipmentList) {
            const container = document.getElementById('equipment-container');
            if (!container || !equipmentList) return;

            container.innerHTML = '';
            equipmentList.forEach(item => {
                const div = document.createElement('div');
                div.className = 'equipment-item mb-2 p-1 border rounded';
                div.innerHTML = `
            <label class="flex items-center">
                <input type="checkbox" name="equipment" value="${item.id}"
                    class="equipment-checkbox mr-2 border rounded"
                    data-price-hour="${item.price_per_hour}"
                    data-price-half-hour="${item.price_per_half_hour}">
                <span class="font-medium">${item.name}</span>
            </label>
            ${item.description ? `<p class="text-sm text-gray-500 mt-1">${item.description}</p>` : ''}
        `;
                container.appendChild(div);
            });

            document.querySelectorAll('.equipment-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', () => updateBookingCost());
            });
        }

        async function updateBookingCost({
                                             tablePriceHour = parseFloat(elements.bookingForm.dataset.pricePerHour),
                                             tablePriceHalfHour = parseFloat(elements.bookingForm.dataset.pricePerHalfHour),
                                             tariffName = "Стандартный тариф"
                                         } = {}) {
            try {
                const duration = parseInt(elements.duration?.value) || 60;
                const blocks = Math.ceil(duration / 30);

                // Стол
                let tableCost = 0;
                if (duration <= 30) {
                    tableCost = tablePriceHalfHour;
                } else if (duration === 60) {
                    tableCost = tablePriceHour;
                } else {
                    const hours = Math.floor(duration / 60);
                    const extra = Math.ceil((duration % 60) / 30);
                    tableCost = (hours * tablePriceHour) + (extra * tablePriceHalfHour);
                }

                // Оборудование
                const equipmentCost = [...document.querySelectorAll('.equipment-checkbox:checked')].reduce((sum, el) => {
                    const priceHalf = parseFloat(el.dataset.priceHalfHour) || 0;
                    const priceHour = parseFloat(el.dataset.priceHour) || priceHalf * 2;
                    let cost = 0;

                    if (duration <= 30) {
                        cost = priceHalf;
                    } else if (duration === 60) {
                        cost = priceHour;
                    } else {
                        const hours = Math.floor(duration / 60);
                        const extra = Math.ceil((duration % 60) / 30);
                        cost = (hours * priceHour) + (extra * priceHalf);
                    }

                    return sum + cost;
                }, 0);

                const totalCost = Math.round(tableCost + equipmentCost);

                updateTariffSummary(
                    tariffName,
                    Math.round(tableCost),
                    Math.round(equipmentCost),
                    totalCost
                );

                updateCostDisplay({
                    table_cost: Math.round(tableCost),
                    equipment_cost: Math.round(equipmentCost),
                    total_cost: totalCost
                });

            } catch (error) {
                console.error('Ошибка расчета стоимости:', error);
                showNotification(`Ошибка расчета стоимости: ${error.message}`, 'error');
            }
        }

        function updateDurationOptions(minMinutes, maxMinutes) {
            const select = document.getElementById('duration-select');
            if (!select) return;

            select.innerHTML = ''; // Очищаем
            for (let mins = minMinutes; mins <= maxMinutes; mins += 30) {
                const option = document.createElement('option');
                option.value = mins;
                option.textContent = `${mins} мин`;
                select.appendChild(option);
            }

            select.value = minMinutes; // По умолчанию — минимальное значение
        }

        // Закрытие модального окна
        function closeModal() {
            elements.modal.classList.add('hidden');
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
                // Получаем выбранную длительность в минутах
                const durationHours = parseFloat(elements.duration.value);
                ///  const durationMinutes = Math.round(durationHours * 60);
                const durationMinutes = parseInt(elements.duration.value) || 60;

                // Собираем данные оборудования с количеством
                const equipmentData = Array.from(document.querySelectorAll('.equipment-checkbox:checked'))
                    .map(checkbox => {
                        const quantityEl = checkbox.closest('.equipment-item').querySelector('select');
                        const quantity = quantityEl ? parseInt(quantityEl.value) : 1;
                        return {
                            id: parseInt(checkbox.value),
                            quantity: quantity
                        };
                    });

                const formData = {
                    date: elements.bookingDate.value,
                    start_time: elements.startTime.value,
                    duration: durationMinutes, // отправляем в минутах
                    table_id: parseInt(elements.tableSelect.value),
                    equipment: equipmentData,
                    participants: parseInt(elements.participants.value),
                    is_group: document.getElementById('is-group').checked,
                    notes: elements.notes.value,
                    slot_id: elements.bookingForm.dataset.slotId || null
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
                    showNotification('Бронирование успешно создано!', 'success');
                    closeModal();
                    await renderCalendar();
                    await loadUserBookings();
                } else {
                    throw new Error(result.error || 'Неизвестная ошибка');
                }

            } catch (error) {
                console.error('Ошибка бронирования:', error);
                showNotification('Ошибка: ' + error.message, 'error');
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


        function updateDateInput() {
            if (elements.bookingDate) {
                elements.bookingDate.valueAsDate = state.currentDate;
            }
        }

        // Навигация по календарю
        async function navigate(direction) {
            const newDate = new Date(state.currentDate);

            switch (state.currentView) {
                case 'day':
                    newDate.setDate(newDate.getDate() + direction);
                    break;
                case 'week':
                    newDate.setDate(newDate.getDate() + (7 * direction));
                    break;
                case 'month':
                    const originalDate = newDate.getDate();
                    newDate.setDate(1);
                    newDate.setMonth(newDate.getMonth() + direction);
                    const daysInNewMonth = new Date(newDate.getFullYear(), newDate.getMonth() + 1, 0).getDate();
                    newDate.setDate(Math.min(originalDate, daysInNewMonth));
                    break;
            }

            state.currentDate = newDate;
            //  if (elements.bookingDate) {
            //     elements.bookingDate.valueAsDate = newDate;
            // }
            updateDateInput();
            updateUI();

            // Загружаем настройки и ждем завершения
            await loadSiteSettings(newDate);

            // Только после загрузки настроек рендерим календарь
            renderCalendar();
        }

        function resetCostDisplay() {
            if (elements.costDisplay.table) {
                elements.costDisplay.table.textContent = '—';
            }
            if (elements.costDisplay.equipment) {
                elements.costDisplay.equipment.textContent = '—';
            }
            if (elements.costDisplay.total) {
                elements.costDisplay.total.textContent = '—';
            }
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
                const dateStr = formatDateForAPI(state.currentDate);
                elements.prevBtn.dataset.date = dateStr;
                elements.nextBtn.dataset.date = dateStr;
            }
        }

        function formatDateForAPI(date) {
            return date.toISOString().split('T')[0];
        }

        // Обновление заголовка календаря
        function updateCalendarTitle() {
            const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

            const daysShort = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

            const date = state.currentDate;

            let title = '';

            switch (state.currentView) {
                case 'day': {
                    const dayShort = daysShort[date.getDay()]; // getDay: 0=Вс,1=Пн,...6=Сб
                    title = `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} ${dayShort}`;
                    break;
                }
                case 'week': {
                    const weekStart = new Date(date);

                    let day = weekStart.getDay();
                    if (day === 0) day = 7; // В JS неделя начинается с Вс=0, поправим на Пн=1
                    weekStart.setDate(weekStart.getDate() - (day - 1));

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

        // Основной рендеринг календаря
        function getMonday(date) {
            const d = new Date(date);
            const day = d.getDay();
            const diff = (day === 0 ? -6 : 1) - day; // Если воскресенье (0), двигаем назад на 6 дней
            d.setDate(d.getDate() + diff);
            return d;
        }

        async function renderCalendar() {
            try {
                const container = elements[`${state.currentView}Container`];
                container.innerHTML = '<div class="text-center py-4">Загрузка...</div>';
                if (!state.siteSettings.is_open && state.currentView === 'day') {
                    container.innerHTML = `
                <div class="p-8 text-center">
                    <div class="inline-block p-6 bg-gray-100 rounded-lg">
                        <i class="fas fa-calendar-times text-4xl text-gray-400 mb-4"></i>
                        <h3 class="text-xl font-medium text-gray-700">Клуб закрыт</h3>
                        <p class="text-gray-500 mt-2">${formatDate(state.currentDate)}</p>
                    </div>
                </div>
            `;
                    return;
                }
                let dateForAPI = state.currentDate;
                if (state.currentView === 'week') {
                    dateForAPI = getMonday(state.currentDate);
                }

                const params = new URLSearchParams({
                    date: formatDateForAPI(dateForAPI),
                    view: state.currentView,
                    table: elements.tableFilter?.value || 'all',
                    status: elements.statusFilter?.value || 'all'
                });

                const response = await fetch(`${API_ENDPOINTS.CALENDAR}?${params}`);
                if (!response.ok) throw new Error('Ошибка загрузки календаря');

                const data = await response.json();

                renderView(data);
            } catch (error) {
                console.error('Ошибка рендеринга календаря:', error);
                showError('Не удалось загрузить данные календаря');
                elements.monthContainer.innerHTML = `
      <div class="p-4 text-center text-red-500">
        Ошибка загрузки: ${error.message}
      </div>
    `;
            }
        }


        // Рендеринг нужного представления
        function renderView(data) {
            const container = elements[`${state.currentView}Container`];
            if (!container) return;

            switch (state.currentView) {
                case 'day':
                    container.innerHTML = generateDayView(data);
                    break;
                case 'week':
                    container.innerHTML = renderWeekView(data);
                    if (elements.userBookingsContainer) {
                        elements.userBookingsContainer.innerHTML = renderUserBookings(data.user_bookings);
                    }
                    attachWeekSlotListeners();
                    break;
                case 'month':
                    container.innerHTML = generateMonthView(data);
                    break;
            }
        }

        // Дневное представление
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

            // Просто выводим все слоты по порядку
            const rows = data.time_slots.map(slotTime => {
                return renderSlotRow(slotTime, data);
            }).join('');

            return `
        <div class="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
            ${renderDayHeader(data.tables)}
            ${rows}
        </div>
    `;
        }

        function renderSlotRow(slotTime, data) {
            const [hours, minutes] = slotTime.split(':').map(Number);
            const slotDate = new Date(data.date);
            slotDate.setHours(hours, minutes, 0, 0);

            // Получаем время закрытия
            const [closeHour, closeMinute] = state.siteSettings.close_time.split(':').map(Number);
            const closeDate = new Date(data.date);
            closeDate.setHours(closeHour, closeMinute, 0, 0);
            const slotDuration = data.slot_duration || 60; // Минуты

            // Проверяем, не выходит ли слот за время закрытия
            const slotEnd = new Date(slotDate);
            slotEnd.setMinutes(slotEnd.getMinutes() + slotDuration);

            // Проверяем, является ли слот прошедшим временем
            const isPast = isPastTime(data.date, slotTime);

            // Если слот выходит за время закрытия или является прошедшим - скрываем его
            if (slotEnd > closeDate || isPast) {
                return ''; // Пропускаем слоты, которые выходят за время закрытия или уже прошли
            }

            return `
<div class="flex border-b border-gray-200 hover:bg-gray-50 booking-slot-row">
    <div class="w-24 md:w-32 p-3 text-right text-sm font-semibold text-gray-700">${slotTime}</div>
    <div class="flex-1 grid grid-cols-${data.tables.length} divide-x divide-gray-200">
        ${data.tables.map(table => {
                const slot = renderSlotCell(data, table.id, slotTime);
                return slot;
            }).join('')}
    </div>
</div>
`;
        }

        function renderDayHeader(tables) {
            return `
        <div class="flex border-b border-gray-200 bg-gray-50">
            <div class="w-24 md:w-32 p-3">Время</div>
            ${tables.map(table => `
                <div class="flex-1 p-3 text-center font-medium">
                    Стол #${table.number}<br>
                    <span class="text-sm text-gray-500">${table.table_type}</span>
                </div>
            `).join('')}
        </div>
    `;
        }

        function renderSlotCell(data, tableId, slotTime) {
            const slot = data.day_schedule[tableId]?.[slotTime] || null;
            const now = new Date();
            const selectedDate = new Date(data.date);
            const [slotHour, slotMinute] = slotTime.split(':').map(Number);
            const slotDate = new Date(selectedDate);
            slotDate.setHours(slotHour, slotMinute, 0, 0);

            const isPast = slotDate < now;

            const closingTime = state.siteSettings.close_time || "22:00";
            const [closingHour, closingMinute] = closingTime.split(':').map(Number);
            const closingDate = new Date(selectedDate);
            closingDate.setHours(closingHour, closingMinute, 0, 0);

            let status, isAvailable, cellClass, textClass, pointerClass;

            // 👇 Показываем "Прошло" только для админа
            if (isPast) {
                if (!state.isAdmin) return '';  // скрыть от обычных пользователей

                status = 'Прошло';
                isAvailable = false;
                cellClass = 'bg-gray-200';
                textClass = 'text-gray-500 italic';
                pointerClass = 'cursor-default pointer-events-none';
            } else if (slot && slot.status !== 'available') {
                status = slot.status || 'Занято';
                isAvailable = false;
                cellClass = 'bg-red-100';
                textClass = 'text-red-800';
                pointerClass = 'cursor-default pointer-events-none';
            } else if (slotDate >= closingDate) {
                status = 'закрыто';
                isAvailable = false;
                cellClass = 'bg-gray-100';
                textClass = 'text-gray-500';
                pointerClass = 'cursor-default pointer-events-none';
            } else {
                status = 'Свободно';
                isAvailable = true;
                cellClass = 'bg-green-100 hover:bg-green-200';
                textClass = 'text-green-800';
                pointerClass = 'cursor-pointer';
            }

            return `
<div class="flex items-center justify-center border-b mt-1 ml-1 rounded-xl p-2 min-h-12 ${cellClass} ${pointerClass} ${isAvailable ? 'booking-slot-available' : ''}"
     data-date="${data.date}" 
     data-time="${slotTime}" 
     data-table="${tableId}" 
     data-slot-id="${slot?.slot_id || ''}">
    <span class="text-sm ${textClass}">${status}</span>
</div>
`;
        }

        function renderWeekView(data) {
            if (!data.days || !data.tables) {
                return '<div class="p-4 text-center text-gray-500">Нет данных для отображения</div>';
            }

            const daysArray = Object.entries(data.days).map(([date, dayData]) => ({
                date, ...dayData
            }));

            const header = `
        <div class="grid grid-cols-${daysArray.length + 1} gap-2  mb-2 text-sm font-medium">
            <div class="bg-white p-2"></div>
            ${daysArray.map(day => `
                <div class="bg-white p-2 text-center rounded-xl">
                    <div>${new Date(day.date).toLocaleDateString('ru-RU', {weekday: 'short'})}</div>
                    <div>${new Date(day.date).getDate()}</div>
                </div>
            `).join('')}
        </div>
    `;

            const body = `
        <div class="grid grid-cols-${daysArray.length + 1} gap-2 bg-gray-200 text-sm">
            ${renderWeekTablesColumn(data.tables)}
            ${daysArray.map(day => renderWeekDayColumn(data, day)).join('')}
        </div>
    `;

            return header + body;
        }

        function renderWeekTablesColumn(tables) {
            return `
        <div class="flex flex-col gap-y-2">
            ${tables.map(table => `
                <div class="bg-white p-2 h-14 mt-1  border-b rounded-xl flex flex-col text-right justify-center shadow-sm">
                    <div class="font-medium">Стол #${table.number}</div>
                    <div class="text-xs text-gray-500">${table.table_type}</div>
                </div>
            `).join('')}
        </div>
    `;
        }

        function renderWeekDayColumn(data, day) {
            const today = new Date();
            const dayDate = new Date(day.date);
            // Сравниваем только даты без времени
            const isPastDay = dayDate < new Date(today.getFullYear(), today.getMonth(), today.getDate());

            return `
        <div class="flex flex-col gap-y-2">
            ${data.tables.map(table => {
                const tableSchedule = day.day_schedule?.[table.id] || {};
                const slotEntries = Object.entries(tableSchedule).filter(([key]) => key !== '_meta');

                if (!day.is_working_day || !slotEntries.length) {
                    return `<div class="bg-gray-100 mt-1 text-gray-400 h-14 border-b rounded-xl flex text-right justify-center shadow-sm">–</div>`;
                }

                const booked = slotEntries.filter(([_, slot]) => slot.status !== 'available').length;
                const total = slotEntries.length;
                const statusClass = booked === total ? 'bg-red-100 text-red-800' : booked > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800';

                // Для прошедших дней и обычных пользователей делаем неактивный слот
                const isDisabled = isPastDay && !state.isAdmin;
                const disabledClass = isDisabled ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : statusClass;
                const pointerEvents = isDisabled ? 'pointer-events-none' : '';

                return `<div class="h-14 border-b flex mt-1  items-center justify-center rounded-xl cursor-pointer px-2 py-1 shadow-sm ${disabledClass} ${pointerEvents} slot-available"
                             title="Занято ${booked} из ${total}"
                             data-date="${day.date}"
                             data-table="${table.id}">
                             ${booked}/${total}
                        </div>`;
            }).join('')}
        </div>
    `;
        }


        function generateMonthView(data) {
            if (!data.weeks || !data.tables) {
                return '<div class="p-4 text-center text-gray-500">Нет данных для отображения</div>';
            }

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const monthStart = data.month ? new Date(data.month + '-01') : new Date();

            const bookingsByDate = {};
            if (data.user_bookings) {
                data.user_bookings.forEach(booking => {
                    if (booking.date) {
                        bookingsByDate[booking.date] = bookingsByDate[booking.date] || [];
                        bookingsByDate[booking.date].push(booking);
                    }
                });
            }

            const getDayClasses = (dayObj, isCurrentMonth) => {
                if (!dayObj || !dayObj.date) return 'bg-gray-100 text-gray-400 rounded p-2 text-sm';

                const date = new Date(dayObj.date);
                if (isNaN(date.getTime())) return 'bg-gray-100 text-gray-400 rounded p-2 text-sm';

                date.setHours(0, 0, 0, 0);

                const isToday = date.toDateString() === today.toDateString();
                const isPast = date < today;

                const isWorkingDay = dayObj.is_working_day ?? true;
                const isShortenedDay = dayObj.shortened ?? false;

                let classes = 'rounded p-2 text-sm';

                if (!isCurrentMonth) {
                    return `${classes} bg-gray-100 text-gray-400`;
                }

                if (!isWorkingDay) {
                    classes += ' bg-red-50 border border-red-100 text-red-800';
                } else if (isShortenedDay) {
                    classes += ' bg-yellow-50 border border-yellow-100 text-yellow-800';
                } else if (isToday) {
                    classes += ' bg-blue-50 border border-blue-200 text-blue-800';
                } else if (isPast) {
                    classes += ' bg-gray-100 text-gray-500';
                } else {
                    classes += ' bg-white border border-gray-200 hover:bg-gray-50';
                }

                if (!isPast && isCurrentMonth && isWorkingDay && !isShortenedDay) {
                    classes += ' cursor-pointer';
                }

                return classes;
            };

            const renderBookingsInfo = (dayObj) => {
                if (!dayObj || !dayObj.date) return '';

                const date = new Date(dayObj.date);
                if (isNaN(date.getTime())) return '';

                date.setHours(0, 0, 0, 0);
                const isPast = date < today;

                const isWorkingDay = dayObj.is_working_day ?? true;
                const isShortenedDay = dayObj.shortened ?? false;
                const workingHours = dayObj.working_hours;

                if (!isWorkingDay) {
                    return '<div class="text-xs text-red-600 mt-1">Выходной</div>';
                }

                if (isShortenedDay) {
                    return `<div class="text-xs text-yellow-600 mt-1">Сокращенный день (${workingHours?.open_time ?? '?'}-${workingHours?.close_time ?? '?'})</div>`;
                }

                const bookings = bookingsByDate[dayObj.date] || [];
                const count = bookings.length;

                if (count === 0) {
                    return '<div class="text-xs text-gray-500 mt-1">Нет бронирований</div>';
                }

                const textColor = isPast ? 'text-gray-400' : 'text-green-600';
                return `<div class="text-xs ${textColor} mt-1">${count} бронирование${count > 1 ? 'й' : ''}</div>`;
            };

            const weekdaysHeader = `
        <div class="grid grid-cols-7 gap-2 mb-4">
            <div class="text-center font-medium">Пн</div>
            <div class="text-center font-medium">Вт</div>
            <div class="text-center font-medium">Ср</div>
            <div class="text-center font-medium">Чт</div>
            <div class="text-center font-medium">Пт</div>
            <div class="text-center font-medium">Сб</div>
            <div class="text-center font-medium">Вс</div>
        </div>
    `;

            const calendarDays = data.weeks.map(week => {
                return `
            <div class="grid grid-cols-7 gap-2">
                ${week.map(dayObj => {
                    if (!dayObj || !dayObj.date) return '<div class="p-2"></div>';

                    const date = new Date(dayObj.date);
                    if (isNaN(date.getTime())) return '<div class="p-2"></div>';

                    const dayOfMonth = date.getDate();
                    const isCurrentMonth = date.getMonth() === monthStart.getMonth();

                    return `
                        <div class="${getDayClasses(dayObj, isCurrentMonth)}" data-date="${dayObj.date}">
                            <div class="font-medium">${dayOfMonth}</div>
                            ${renderBookingsInfo(dayObj)}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
            }).join('');

            return `
        <div class="calendar-container">
            ${weekdaysHeader}
            ${calendarDays}
        </div>
    `;
        }

        function cancelBooking(bookingId) {
            if (confirm('Вы уверены, что хотите отменить бронирование?')) {
                fetch(`${API_ENDPOINTS.BOOKINGS}${bookingId}/`, {
                    method: 'DELETE', headers: {
                        'X-CSRFToken': getCSRFToken()
                    }
                })
                    .then(response => {
                        if (response.ok) {
                            alert('Бронирование успешно отменено');
                            renderCalendar();
                        } else {
                            throw new Error('Ошибка при отмене бронирования');
                        }
                    })
                    .catch(error => {
                        console.error(error);
                        showError(error.message);
                    });
            }
        }

        const freeSlots = document.querySelectorAll('.bg-green-100.cursor-pointer');
        freeSlots.forEach(slot => {
            slot.addEventListener('click', function () {
                // Получаем данные о времени и столе из атрибутов
                const time = this.getAttribute('data-time');
                const table = this.getAttribute('data-table');

                // Устанавливаем значения в форме бронирования
                if (time && table) {
                    // Устанавливаем текущую дату
                    const today = new Date();
                    const dateString = today.toISOString().split('T')[0];
                    document.getElementById('booking-date').value = dateString;

                    // Устанавливаем выбранное время
                    document.getElementById('booking-start-time').value = time;

                    // Устанавливаем выбранный стол
                    document.getElementById('booking-table').value = table;

                    // Открываем модальное окно
                    bookingModal.classList.remove('hidden');

                    // Обновляем стоимость
                    updateBookingCost();
                }
            });
        });

        function payBooking(bookingId) {
            // Реализация оплаты бронирования
            alert(`Оплата бронирования #${bookingId}`);
        }


        // Отображение бронирований пользователя
        function renderUserBookings(bookings) {
            if (!bookings?.length) {
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
                    ${bookings.map(b => `
                        <tr>
                            <td class="px-3 py-2 border">${new Date(b.date).toLocaleDateString('ru-RU')}</td>
                            <td class="px-3 py-2 border">${b.start}-${b.end}</td>
                            <td class="px-3 py-2 border">#${b.table_number}</td>
                            <td class="px-3 py-2 border">${b.status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        }

        // Обработчики слотов недели
        function attachWeekSlotListeners() {
            document.querySelectorAll('.slot-available').forEach(cell => {
                cell.addEventListener('click', () => {
                    const {date, table} = cell.dataset;
                    openBookingModal(date, null, table, null);
                });
            });
        }

        function formatDate(dateStr) {
            const d = new Date(dateStr);
            return isNaN(d) ? dateStr : `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth() + 1).toString().padStart(2, '0')}.${d.getFullYear()}`;
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
    }
)
;