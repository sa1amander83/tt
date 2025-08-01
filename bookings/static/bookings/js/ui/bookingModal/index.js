import {$, $$} from '../../utils/dom.js';
import {BookingAPI} from '../../api/booking.js';

import {updateCost} from "./cost.js";
import {CalendarUI} from "../calendar/index.js";
import {CalendarAPI} from "../../api/calendar.js";
import {EquipmentAPI} from '../../api/equipment.js';
import {PromoAPI} from "../../api/promo.js";

export const BookingModal = {
    store: null,


    init(store) {
        this.store = store;
        $('#booking-form')?.addEventListener('submit', (e) => this.submit(e));
        $('#close-modal')?.addEventListener('click', () => this.close());
        $('#cancel-booking')?.addEventListener('click', () => this.close());
        $('#apply-promo-btn')?.addEventListener('click', () => this.applyPromoCode());
        // $('#apply-promo-btn')?.addEventListener('click', async () => {
        //     const code = $('#promo-code')?.value.trim();
        //     const userId = window.CURRENT_USER_ID || null;
        //
        //     if (!code) return;
        //
        //     const res = await PromoAPI.validate(code, userId);
        //     const msg = $('#promo-code-message');
        //
        //     if (res.valid) {
        //         this.store.set({promoCode: res, promoApplied: true});
        //         msg.textContent = res.description;
        //         msg.className = 'text-xs text-green-600';
        //         this.updateBookingCost();
        //     } else {
        //         msg.textContent = res.message || 'Неверный промокод';
        //         msg.className = 'text-xs text-red-600';
        //     }
        // });

    },

    close() {
        $('#booking-modal')?.classList.add('hidden');
    },

    async open({date, time, tableId}) {
        // 1. Если настроек нет или дата другая — подгружаем
        let {settings} = this.store.get();
        if (!settings?.open_time || settings.date !== date) {
            settings = await CalendarAPI.settings(new Date(date));
            this.store.set({settings});
        }
        const tables = await fetch('api/tables/');
        const tablesData = await tables.json();
        this.store.set({tables: tablesData});
        // 🔁 2. Загружаем тарифы, если ещё не загружены

        let {pricing} = this.store.get();
        if (!pricing || pricing.length === 0) {
            const ratesResponse = await fetch('api/rates/');
            const ratesData = await ratesResponse.json();

            // Сохраняем все тарифы и типы столов
            this.store.set({
                table_types: ratesData.table_types,
                pricing: ratesData.pricing_plans || [ratesData] // учитываем разные форматы ответа
            });
        }

        async function fetchPrice(date, time, tableId, duration) {
            const res = await fetch(`/bookings/api/get-booking-info/?date=${date}&time=${time}&table_id=${tableId}&duration=${duration}`);
            if (!res.ok) throw new Error('Не удалось получить цену');
            return res.json();
        }

        // 3. Загружаем оборудование
        const equipment = await EquipmentAPI.list();
        this.populateEquipmentOptions(equipment);

        // 4. Сохраняем слот
        this.slot = {date, time, tableId};

        // 5. Заполняем форму
        this.populateTableSelect(tableId);
        this.populateTimeSelect(time);
        this.populateParticipants(tableId);

        $('#booking-date').value = date;
        await this.updateBookingCost();
        // 6. Показываем окно
        $('#booking-modal').classList.remove('hidden');

        // 7. Слушатели
        $('#booking-duration')?.addEventListener('change', () => this.updateBookingCost());
        $('#booking-table')?.addEventListener('change', () => this.updateBookingCost());
        $('#participants')?.addEventListener('change', () => this.updateBookingCost());
    },

    async applyPromoCode() {
        const promoCode = $('#promo-code').value.trim();
        if (!promoCode) return;

        try {
            const response = await fetch('/api/bookings/check-promo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({promo_code: promoCode})
            });

            const data = await response.json();

            if (response.ok) {
                // Промокод действителен
                $('#promo-code-message').classList.add('hidden');
                this.store.set({promoCode: data});
                this.updateBookingCost();
            } else {
                // Промокод недействителен
                $('#promo-code-message').textContent = data.error || 'Недействительный промокод';
                $('#promo-code-message').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error applying promo code:', error);
            $('#promo-code-message').textContent = 'Ошибка при проверке промокода';
            $('#promo-code-message').classList.remove('hidden');
        }
    },
    populateTableSelect(defaultId) {
        const {tables, table_types} = this.store.get();
        const sel = $('#booking-table');
        sel.innerHTML = '';

        tables.forEach(t => {
            // Добавляем проверку на существование table_type
            const tableType = t.table_type || {};
            const tableTypeId = tableType.id ? Number(tableType.id) : null;

            // Находим соответствующий тип стола в table_types
            const typeInfo = table_types?.find(p => p.id === tableTypeId);
            const price = typeInfo?.hour_rate || 0;
            const capacity = tableType.max_capacity || 2; // Значение по умолчанию

            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = `${t.number}${tableType.name ? ` - ${tableType.name}` : ''}`;
            opt.dataset.price = price;
            opt.dataset.capacity = capacity;
            sel.appendChild(opt);
        });

        sel.value = String(defaultId);
        this.populateParticipants(sel.value);
        sel.addEventListener('change', () => this.populateParticipants(sel.value));
    },
    populateTimeSelect(defaultTime) {
        const {settings} = this.store.get();

        const open = settings?.current_day?.open_time ?? '09:00';
        const close = settings?.current_day?.close_time ?? '22:00';
        const [openH, openM] = open.split(':').map(Number);
        const [closeH, closeM] = close.split(':').map(Number);

        const sel = $('#booking-start-time');
        sel.innerHTML = '';

        let dt = new Date();
        dt.setHours(openH, openM, 0, 0);

        const step = 30;
        const last = new Date();
        last.setHours(closeH, closeM, 0, 0);
        last.setMinutes(last.getMinutes() - step);

        while (dt <= last) {
            const t = dt.toTimeString().slice(0, 5);
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            opt.selected = t === defaultTime;
            sel.appendChild(opt);
            dt.setMinutes(dt.getMinutes() + step);
        }
    },
    populateParticipants(tableId) {
        const sel = $('#participants');
        const table = this.store.get().tables.find(t => String(t.id) === String(tableId));


        if (!table) return;

        sel.innerHTML = '';
        for (let i = 1; i <= table.capacity; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            sel.appendChild(opt);
        }
        sel.value = Math.min(2, table.capacity); // дефолт 2, но не больше max
    },
    populateEquipmentOptions(list) {
        const container = $('#equipment-container');
        container.addEventListener('change', () => this.updateBookingCost());
        container.innerHTML = '';
        list.forEach(item => {
            const div = document.createElement('div');
            div.className = 'equipment-item mb-2';
            div.innerHTML = `
      <label class="flex items-center">
        <input type="checkbox" name="equipment" value="${item.id}"
               class="equipment-checkbox mr-2 border-2 border-green-500"
               data-price-hour="${item.price_per_hour}"
               data-price-half-hour="${item.price_per_half_hour}">
        <span>${item.name}</span>
      </label>
    `;
            container.appendChild(div);
        });

    },
    populateForm() {
        const {date, time, tableId} = this.slot;
        $('#booking-date').value = date;
        $('#booking-start-time').value = time;
        $('#booking-table').value = String(tableId);
        updateCost(this.store);
    },
    getActivePricingPlanForDateTime(dateStr, timeStr) {
        const allPlans = this.store.get().pricing || [];

        const date = new Date(`${dateStr}T${timeStr}`);
        let matchedPlan = null;

        for (const plan of allPlans) {
            const from = new Date(`${plan.valid_from}T00:00:00`);
            const to = plan.valid_to ? new Date(`${plan.valid_to}T23:59:59`) : null;

            if (date >= from && (!to || date <= to)) {
                matchedPlan = plan;
                break; // можно доработать при наличии времени начала/окончания тарифа
            }
        }

        return matchedPlan;
    },
    async fetchBookingInfo({date, time, tableId, duration, isGroup = false, equipment = []}) {
        const params = new URLSearchParams({
            date,
            time,
            table_id: tableId,
            duration,
            is_group: isGroup ? 'true' : 'false',
            equipment: JSON.stringify(equipment)
        });

        const res = await fetch(`/bookings/api/get-booking-info/?${params.toString()}`);
        if (!res.ok) throw new Error('Ошибка при получении информации о бронировании');
        return await res.json();
    },
    async submit(e) {
        e.preventDefault();

        const fd = new FormData(e.target);
        const payload = Object.fromEntries(fd.entries());
        const {promoCode} = this.store.get();


        // Добавьте промокод в payload, если он есть
        if (promoCode) {
            payload.promo_code = promoCode.code;
        }
        payload.table_id = Number(payload.table_id);
        payload.duration = Number(payload.duration);
        payload.participants = Number(payload.participants);
        payload.date = this.slot.date;
        payload.start_time = this.slot.time;
        payload.equipment = [...$$('.equipment-checkbox:checked')]
            .map(cb => ({id: Number(cb.value), quantity: 1}));
        payload.slot_id = elements.bookingForm.dataset.slotId || null;

        const {booking_id} = await BookingAPI.create(payload);
        await BookingAPI.payment(booking_id);

        this.close();
        await CalendarUI.render();
    },
    async updateBookingCost() {
        const date = $('#booking-date')?.value;
        const time = $('#booking-start-time')?.value;
        const durationHours = parseInt($('#booking-duration')?.value || 1);
        const duration = durationHours * 60;

        const selectedOption = $('#booking-table')?.selectedOptions?.[0];
        if (!selectedOption) {
            console.warn("Не выбран стол");
            return;
        }

        const tableId = selectedOption.value;
        const isGroup = $('#is-group')?.checked || false;

        // Собираем оборудование
        const equipment = [...$$('.equipment-checkbox:checked')].map(el => ({
            id: Number(el.value),
            quantity: 1 // в будущем можно подставить значение из select
        }));

        try {
            // Получаем данные с сервера
            const params = new URLSearchParams({
                date,
                time,
                table_id: tableId,
                duration: duration.toString(),
                is_group: isGroup ? 'true' : 'false',
                equipment: JSON.stringify(equipment)
            });

            const res = await fetch(`api/get-booking-info/?${params.toString()}`);
            if (!res.ok) throw new Error("Ошибка при получении информации о бронировании");
            const data = await res.json();

            // Применим промокод, если он есть и применён
            let discountMultiplier = 1;
            const promo = this.store.get().promoCode;
            if (this.store.get().promoApplied && promo?.discount_percent) {
                discountMultiplier = (100 - promo.discount_percent) / 100;
            }

            // Обновляем UI
            $('#tariff-name').textContent = data.tariff_description || data.pricing_plan || 'Стандартный тариф';
            $('#tariff-table-cost').textContent = `${Math.round(data.base_price)} ₽`;
            $('#tariff-equipment-cost').textContent = `${Math.round(data.equipment_price || 0)} ₽`;
            $('#tariff-total-cost').textContent = `${Math.round(data.final_price * discountMultiplier)} ₽`;
            $('#tariff-summary')?.classList.remove('hidden');

        } catch (err) {
            console.error("Ошибка при расчёте стоимости:", err);

            // При ошибке — скрыть расчёты
            $('#tariff-name').textContent = 'Ошибка загрузки тарифа';
            $('#tariff-summary')?.classList.add('hidden');
        }
    }

};

