import {$, $$} from '../../utils/dom.js';
import {BookingAPI} from '../../api/booking.js';
import {CalendarUI} from '../calendar/index.js';
import {CalendarAPI} from "../../api/calendar.js";
import {EquipmentAPI} from '../../api/equipment.js';
import {csrfToken} from "../../utils/getcsrf.js";


export const BookingModal = {
    store: null,


    init(store) {
        this.store = store;
        $('#booking-form')?.addEventListener('submit', (e) => this.submit(e));
        $('#close-modal')?.addEventListener('click', () => this.close());
        $('#cancel-booking')?.addEventListener('click', () => this.close());


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


        const schedule = await CalendarAPI.schedule(new Date(date));
        this.store.set({schedule});
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
        $('#booking-table')?.addEventListener('change', () => {
            this.populateParticipants($('#booking-table').value);
            this.populateTimeSelect($('#booking-start-time').value); // Сохраняем текущее выбранное время
            this.updateBookingCost();
        });
        document.getElementById("apply-promo-btn").addEventListener("click", async () => {
                const codeInput = document.getElementById("promo-code");
                const message = document.getElementById("promo-code-message");
                const code = codeInput.value.trim().toLowerCase();

                if (!code) {
                    message.textContent = "Введите промокод.";
                    message.classList.remove("hidden");
                    message.classList.replace("text-green-600", "text-red-600");
                    return;
                }

                try {
                    const response = await fetch("/management/validate-promo/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            code: code,
                            user_id: this.store.currentUserId || null
                        })
                    });

                    if (!response.ok) {
                        const text = await response.text();
                        throw new Error(text || "Ошибка сервера");
                    }

                    const data = await response.json();

                    if (!data.valid) {
                        throw new Error(data.error || "Недействительный промокод");
                    }

                    // Сохраняем промокод в состоянии
                    this.store.promoCode = {
                        code: code,
                        discount_percent: data.discount_percent || 0,
                        description: data.description || code,
                        promo_type: data.promo_type || 'percent'
                    };
                    this.store.promoApplied = true;

                    message.textContent = `Промокод применен: ${this.store.promoCode.description}`;

                    message.classList.remove("text-red-600");
                    message.classList.add("text-green-600");
                    message.classList.remove("hidden");
                    // Обновляем стоимость с учетом скидки
                    await this.updateBookingCost();

                } catch (err) {
                    try {
                        const errorJson = JSON.parse(err.message); // err.message — это строка вида '{"error": "..."}'
                        message.textContent = errorJson.error || 'Неверный промокод';
                    } catch (e) {
                        message.textContent = 'Неверный промокод';
                    }

                    message.classList.remove("text-green-600");
                    message.classList.add("text-red-600");
                    message.classList.remove('hidden');
                    return false;
                }

                // Пересчитываем стоимость без скидки
                await this.updateBookingCost();
            }
        )

        $('#participants')?.addEventListener('change', () => this.updateBookingCost());

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
            opt.textContent = `${t.description}`;
            opt.dataset.price = price;
            opt.dataset.capacity = capacity;
            sel.appendChild(opt);
        });

        sel.value = String(defaultId);
        this.populateParticipants(sel.value);
        sel.addEventListener('change', () => this.populateParticipants(sel.value));
    }
    ,
    populateTimeSelect(defaultTime) {
        const {settings} = this.store.get();
        const open = settings?.current_day?.open_time ?? '09:00';
        const close = settings?.current_day?.close_time ?? '22:00';
        const tableId = this.slot?.tableId || $('#booking-table')?.value;

        // Получаем расписание для выбранного стола
        const scheduleData = this.store.get().schedule ?? {};
        const scheduleArray = Array.isArray(scheduleData) ? scheduleData : scheduleData.schedule ?? [];
        const tableSchedule = scheduleArray.find(s => s.table_id === Number(tableId))?.bookings ?? [];

        const sel = $('#booking-start-time');
        sel.innerHTML = '';

        let currentTime = new Date(`${this.slot.date}T${open}`);
        const endTime = new Date(`${this.slot.date}T${close}`);
        const now = new Date();

        const minDuration = 30; // минимальная длительность в минутах
        const step = 30; // шаг в минутах

        while (currentTime < endTime) {
            const timeStr = currentTime.toTimeString().substring(0, 5);

            // Пропускаем прошедшее время
            if (currentTime <= now) {
                currentTime = new Date(currentTime.getTime() + step * 60000);
                continue;
            }

            // Проверяем доступность слота
            let isAvailable = true;
            const slotEnd = new Date(currentTime.getTime() + minDuration * 60000);

            // Проверяем пересечения с существующими бронированиями
            for (const booking of tableSchedule) {
                const bookingStart = new Date(booking.start_time);
                const bookingEnd = new Date(booking.end_time);

                if ((currentTime >= bookingStart && currentTime < bookingEnd) ||
                    (slotEnd > bookingStart && slotEnd <= bookingEnd) ||
                    (currentTime <= bookingStart && slotEnd >= bookingEnd)) {
                    isAvailable = false;
                    break;
                }
            }

            if (isAvailable) {
                const opt = document.createElement('option');
                opt.value = timeStr;
                opt.textContent = timeStr;
                opt.selected = timeStr === defaultTime;
                sel.appendChild(opt);
            }

            currentTime = new Date(currentTime.getTime() + step * 60000);
        }
    }
    ,
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
    }
    ,
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

    }

    // getNextBookingTime(date, time, tableId) {
    //     const {settings} = this.store.get();
    //     const schedule = settings?.current_day?.schedule ?? [];
    //
    //     const tableSchedule = schedule.find(s => s.table_id === Number(tableId))?.bookings || [];
    //     const startTime = new Date(`${date}T${time}`);
    //
    //     // Находим ближайшее бронирование после указанного времени
    //     const nextBooking = tableSchedule
    //         .filter(b => new Date(b.start_time) > startTime)
    //         .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))[0];
    //
    //     return nextBooking ? new Date(nextBooking.start_time) : null;
    // }
    ,
    async updateBookingCost() {

        try {
            const {user} = this.store.get();
            if (!user || !user.isAuthenticated) {
                // Если не залогинен — просто скрыть стоимость и не делать запрос
                $('#tariff-summary')?.classList.add('hidden');
                return;
            }

            const formData = this.getFormPayload();

            // Добавляем проверку duration_minutes
            if (isNaN(formData.duration_minutes) || formData.duration_minutes <= 0) {
                throw new Error('Некорректная длительность бронирования');
            }

            const params = new URLSearchParams({
                date: formData.date,
                time: formData.time,
                table_id: formData.table_id,
                duration: formData.duration_minutes,
                is_group: formData.is_group ? 'true' : 'false',
                equipment: JSON.stringify(formData.equipment)
            });

            const res = await fetch(`api/get-booking-info/?${params.toString()}`);

            if (!res.ok) {
                const text = await res.text();
                throw new Error(`Ошибка сервера: ${res.status} ${res.statusText} — ${text}`);
            }

            const data = await res.json();
            const maxDur = this.getAllowedDurations(formData.time);

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
            console.error('Ошибка при обновлении стоимости бронирования:', err);
            showNotification("Ошибка при расчёте стоимости: " + (err.message || err), 'error');
            $('#tariff-name').textContent = 'Ошибка загрузки тарифа';
            $('#tariff-summary')?.classList.add('hidden');
        }
    },

    async submit(e) {
        e.preventDefault();

        try {
            // Проверяем авторизацию пользователя
            const {user} = this.store.get();
            // if (!user || !user.is_authenticated) {
            //     showNotification('Для бронирования необходимо войти в систему', 'error');
            //     // Перенаправляем на страницу авторизации через 3 секунды
            //     setTimeout(() => {
            //         window.location.href = '/accounts/signin/';
            //     }, 3000);
            //     return;
            // }

            const fd = new FormData(e.target);
            const payload = Object.fromEntries(fd.entries());
            const {promoCode} = this.store.get();

            payload.table_id = Number(payload.table);
            payload.duration = Math.round(Number(payload.duration * 60));
            payload.participants = Number(payload.participants);
            payload.date = this.slot.date;
            payload.start_time = this.slot.time;
            payload.equipment = [...$$('.equipment-checkbox:checked')]
                .map(cb => ({id: Number(cb.value), quantity: 1}));
            payload.slot_id = e.target.dataset.slotId || null;

            if (promoCode) {
                payload.promo_code = promoCode.code;
            }

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

            // if (err?.login_required) {
            //     showNotification('Для бронирования необходимо войти в систему', 'error');
            //     setTimeout(() => {
            //         window.location.href = '/accounts/signin/';
            //     }, 3000);
            //     return;
            // }
        }
    },

    getFormPayload() {
        // Получаем значение duration и преобразуем в число
        const durationValue = $('#booking-duration')?.value;
        const durationHours = parseFloat(durationValue) || 1; // дефолтное значение 1 час, если не число
        const duration_minutes = Math.round(durationHours * 60);

        const equipment = [...$$('.equipment-checkbox:checked')].map(cb => ({
            id: Number(cb.value),
            quantity: 1
        }));

        return {
            date: $('#booking-date')?.value,
            time: $('#booking-start-time')?.value,
            table_id: Number($('#booking-table')?.value),  // <--- именно отсюда брать ID стола
            participants: Number($('#participants')?.value),
            is_group: $('#is-group')?.checked || false,
            duration_minutes,
            equipment
        };
    },


getAllowedDurations(startTimeStr) {
    const {settings} = this.store.get();
    const close = settings?.current_day?.close_time ?? '22:00';
    const date = this.slot?.date || $('#booking-date')?.value;
    const tableId = this.slot?.tableId || Number($('#booking-table')?.value);

    if (!startTimeStr) return [];

    const norm = t => t.length === 5 ? t + ':00' : t;
    const startDt = new Date(`${date}T${norm(startTimeStr)}`);
    const closeDt = new Date(`${date}T${norm(close)}`);

    // 1. до закрытия, но не более 3 часов
    const maxByClose = Math.min(180, Math.floor((closeDt - startDt) / 60000));

    // 2. брони стола
    const schedule = this.store.get().schedule ?? [];
    const bookings = (Array.isArray(schedule) ? schedule : schedule.schedule ?? [])
        .find(s => s.table_id === tableId)?.bookings ?? [];

    // 3. ближайшая граница
    const nextStart = bookings
        .map(b => new Date(`${date}T${norm(b.start_time)}`))
        .find(t => t > startDt);

    const limitMin = nextStart
        ? Math.min(180, Math.floor((nextStart - startDt) / 60000))
        : maxByClose;

    // 4. 30, 60, 90 …
    const step = 30;
    const allowed = [];
    for (let m = step; m <= limitMin; m += step) allowed.push(m);

    return allowed.length ? allowed : [step];
},


   populateDurationOptions() {
    const allowed = this.getAllowedDurations($('#booking-start-time')?.value);
    const sel = $('#booking-duration');
    sel.innerHTML = '';

    allowed.forEach(min => {
        const opt = document.createElement('option');
        opt.value = min / 60;
        opt.textContent = `${Math.floor(min / 60) ? `${Math.floor(min / 60)} ч` : ''}${min % 60 ? ` ${min % 60} мин` : ''}`.trim();
        sel.appendChild(opt);
    });

    // по умолчанию 1 час (60 мин), если есть
    sel.value = allowed.includes(60) ? '1' : (allowed[0] / 60).toString();
}
};

