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
        $('#booking-start-time')?.addEventListener('change', () => this.updateBookingCost());
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
            showNotification('Ошибка применения промокода:', error);
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

    async submit(e) {
        e.preventDefault();

        try {
            const fd = new FormData(e.target);
            const payload = Object.fromEntries(fd.entries());
            const {promoCode} = this.store.get();

            payload.table_id = Number(payload.table);


            payload.duration = Math.round(Number(payload.duration  * 60));


            payload.participants = Number(payload.participants);
            payload.date = this.slot.date;
            payload.start_time = this.slot.time;
            payload.equipment = [...$$('.equipment-checkbox:checked')]
                .map(cb => ({id: Number(cb.value), quantity: 1}));
            payload.slot_id = e.target.dataset.slotId || null;

            if (promoCode) {
                payload.promo_code = promoCode.code;
            }
            console.log(payload);
            const {booking_id} = await BookingAPI.create(payload);
            const paymentRes = await BookingAPI.payment(booking_id);

            if (paymentRes.confirmation_url) {
                window.open(paymentRes.confirmation_url, '_blank');

            } else if (paymentRes.status === 'paid') {
                showNotification('Бронирование успешно оплачено.', 'success');
                this.close();
                await CalendarUI.render();
            } else {
                showNotification('Не удалось инициировать оплату.', 'error');
            }
        } catch (err) {
            console.error('Ошибка при бронировании:', err);

            const message = err?.error || err?.message || 'Неизвестная ошибка при бронировании';
            showNotification(message, 'error');
        }
    },

    getFormPayload() {
        const durationHours = parseFloat($('#booking-duration')?.value);
        const duration_minutes = Math.round(durationHours * 60);

        const equipment = [...$$('.equipment-checkbox:checked')].map(cb => ({
            id: Number(cb.value),
            quantity: 1
        }));

        return {
            date: $('#booking-date')?.value,
            time: $('#booking-start-time')?.value,
            table_id: Number($('#booking-table')?.value),
            participants: Number($('#participants')?.value),
            is_group: $('#is-group')?.checked || false,
            duration_minutes,
            equipment
        };
    },


    async updateBookingCost() {
        const {
            date, time, table_id, duration_minutes, is_group, equipment
        } = this.getFormPayload();

        const params = new URLSearchParams({
            date,
            time,
            table_id,
            duration: duration_minutes,
            is_group: is_group ? 'true' : 'false',
            equipment: JSON.stringify(equipment)
        });

        try {
            const res = await fetch(`api/get-booking-info/?${params.toString()}`);
            if (!res.ok) throw new Error("Ошибка при получении информации о бронировании");

            const data = await res.json();
            const maxDur = this.getMaxDurationMinutes(time);
            const effectiveMax = Math.min(maxDur, data?.max_duration || 180);

            this.populateDurationOptions(data?.min_duration || 30, effectiveMax);

            const promo = this.store.get().promoCode;
            const discountMultiplier = (this.store.get().promoApplied && promo?.discount_percent)
                ? (100 - promo.discount_percent) / 100 : 1;

            $('#tariff-name').textContent = data.tariff_description || data.pricing_plan || 'Стандартный тариф';
            $('#tariff-table-cost').textContent = `${Math.round(data.base_price)} ₽`;
            $('#tariff-equipment-cost').textContent = `${Math.round(data.equipment_price || 0)} ₽`;
            $('#tariff-total-cost').textContent = `${Math.round(data.final_price * discountMultiplier)} ₽`;
            $('#tariff-summary')?.classList.remove('hidden');
        } catch (err) {
            showNotification("Ошибка при расчёте стоимости:", err);
            $('#tariff-name').textContent = 'Ошибка загрузки тарифа';
            $('#tariff-summary')?.classList.add('hidden');
        }
    },
    getMaxDurationMinutes(startTimeStr) {
        const {settings} = this.store.get();
        const close = settings?.current_day?.close_time ?? '22:00';
        const [closeH, closeM] = close.split(':').map(Number);

        // день берём из текущего слота
        const date = this.slot?.date || $('#booking-date')?.value;
        const closeDt = new Date(`${date}T${close}:00`);
        const startDt = new Date(`${date}T${startTimeStr}`);

        const diffMinutes = Math.floor((closeDt - startDt) / 60000);
        return Math.max(diffMinutes, 0); // не меньше 0
    },
    populateDurationOptions(min, max) {
        const select = $('#booking-duration');
        const prev = select.value;
        select.innerHTML = '';

        const step = 30;
        for (let m = min; m <= max; m += step) {
            const opt = document.createElement('option');
            opt.value = m / 60;
            opt.textContent = `${Math.floor(m / 60) ? `${Math.floor(m / 60)} ч` : ''}${m % 60 ? ` ${m % 60} мин` : ''}`.trim();
            select.appendChild(opt);
        }

        select.value = [...select.options].some(o => o.value === prev)
            ? prev
            : max >= 60 ? 1 : max / 60;
    }
};

