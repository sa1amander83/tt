import {Store} from './store/index.js';
import {AuthAPI} from './api/auth.js';
import {CalendarUI} from './ui/calendar/index.js';

import {CalendarAPI} from './api/calendar.js';

import {UserBookings} from './ui/userBookings.js';
import {BookingModal} from "./ui/bookingModal/index.js";

(async () => {
    const store = Store({
        currentDate: new Date(),
        currentView: 'day',
        rates: {},
        tables: [],
        bookings: [],
        settings: {},
        user: null,
        promoCode: null,
        promoApplied: false
    });

    // текущий пользователь
    const user = await AuthAPI.current();
    store.set({user});

    // первичные данные
    const [rates, tables, settings] = await Promise.all([
        CalendarAPI.rates(),
        CalendarAPI.tables(),
        CalendarAPI.settings(store.get().currentDate)
    ]);
    store.set({rates, tables, settings});

    // инициализация UI
    CalendarUI.init(store);
    BookingModal.init(store);
    await UserBookings.init(store);

    await CalendarUI.render();
})();

