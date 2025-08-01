import { get } from './index.js';

export const CalendarAPI = {
  rates    : () => get('/bookings/api/rates/'),
  tables   : () => get('/bookings/api/tables/'),
  settings : (date) => get(`/bookings/api/site-settings/?date=${date.toISOString().slice(0,10)}`),
  data     : (params) => get(`/bookings/api/calendar/?${new URLSearchParams(params)}`)

};

