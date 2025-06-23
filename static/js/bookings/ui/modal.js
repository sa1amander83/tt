export class BookingModal {
    constructor() {
        this.modal = document.getElementById('booking-modal');
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('close-modal')?.addEventListener('click', () => this.close());
        document.getElementById('cancel-booking')?.addEventListener('click', () => this.close());
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
    }

    open(data = {}) {
        this.populateForm(data);
        this.modal.classList.remove('hidden');
    }

    close() {
        this.resetBookingForm();
        this.modal.classList.add('hidden');
    }

    resetBookingForm() {
            // Сброс инпутов формы
            if (elements.bookingDate) elements.bookingDate.value = '';
            if (elements.startTime) elements.startTime.value = '';
            if (elements.participants) elements.participants.value = '2';
            if (elements.notes) elements.notes.value = '';

            // Промокод и сообщение
            const promoCodeInput = document.getElementById('promo-code');
            const promoCodeMessage = document.getElementById('promo-code-message');
            if (promoCodeInput) promoCodeInput.value = '';
            if (promoCodeMessage) promoCodeMessage.classList.add('hidden');

            // Чекбокс "Группа"
            const isGroupCheckbox = document.getElementById('is-group');
            if (isGroupCheckbox) isGroupCheckbox.checked = false;

            // Сброс состояния формы
            if (elements.bookingForm) {
                elements.bookingForm.dataset.slotId = '';
                elements.bookingForm.dataset.discount = '0';
                elements.bookingForm.dataset.pricePerHour = '0';
                elements.bookingForm.dataset.pricePerHalfHour = '0';
            }

            // Сброс состояния приложения
            state.promoCode = null;
            state.promoApplied = false;

            // Очистка UI (если нужно скрыть расчёты и т.п.)
            updateTariffSummary("Стандартный тариф", 0, 0, 0);
            updateCostDisplay({
                table_cost: 0,
                equipment_cost: 0,
                total_cost: 0
            });

            // Очистка списков, если требуется
            populateTimeOptions(new Date(), new Date(), '');     // можно передать фиктивные значения
            populateTableOptions([], null);
            populateParticipants([], null);
            populateDurationOptions(30, 180, 30);  // минимальная заглушка
            populateEquipmentOptions([]);
        }

    populateForm(data) {
        const form = document.getElementById('booking-form');
        form.elements['booking-date'].value = data.date;
        form.elements['booking-start-time'].value = data.start_time;
        form.elements['booking-duration'].value = data.duration;
        form.elements['booking-table'].value = data.table;
        form.elements['booking-equipment'].value = data.equipment;
        form.elements['booking-participants'].value = data.participants;
        form.elements['booking-notes'].value = data.notes;
    }
      populateTimeOptions(openTime, closeTime, selectedTime) {
            const timeSelect = elements.startTime;
            timeSelect.innerHTML = '';

            const optionIntervalMinutes = 30;
            const lastAvailableTime = new Date(closeTime.getTime() - optionIntervalMinutes * 60000);

            let currentTime = new Date(openTime);

            while (currentTime <= lastAvailableTime) {
                const hours = currentTime.getHours().toString().padStart(2, '0');
                const minutes = currentTime.getMinutes().toString().padStart(2, '0');
                const timeString = `${hours}:${minutes}`;

                const option = document.createElement('option');
                option.value = timeString;
                option.textContent = timeString;

                if (timeString === selectedTime) {
                    option.selected = true;
                }

                timeSelect.appendChild(option);
                currentTime = new Date(currentTime.getTime() + optionIntervalMinutes * 60000);
            }
        }

         populateTableOptions(tables, selectedId) {
            const select = elements.tableSelect;
            if (!select) return;

            select.innerHTML = '';
            tables.forEach(table => {
                const option = new Option(`Стол #${table.number} (${table.table_type})`, table.id);
                option.dataset.maxPlayers = table.max_capacity || 2;
                select.add(option);
            });
            select.value = selectedId;

            const selectedTable = tables.find(t => t.id === parseInt(selectedId));
            const tableTypeElement = document.getElementById('table-type-name');
            if (tableTypeElement) {
                tableTypeElement.textContent = selectedTable?.table_type || '';
            }
        }

         populateParticipants(tables, tableId) {
            const select = document.getElementById('participants');
            if (!select) return;

            const table = tables.find(t => t.id === parseInt(tableId));
            const maxPlayers = table?.max_capacity || 2;

            select.innerHTML = '';
            for (let i = 2; i <= maxPlayers; i++) {
                const option = new Option(`${i} игрок${i > 1 ? 'а' : ''}`, i);
                select.add(option);
            }
        }

         populateDurationOptions(min, max, limit) {
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

         populateEquipmentOptions(equipmentList) {
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








}