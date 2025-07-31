import { post } from './index.js';

export const BookingAPI = {
  create : (payload) => post('/bookings/api/create/', payload),
  cancel : (id)     => post(`/bookings/api/create/${id}/`, { _method: 'DELETE' }),
  payment: (id)     => post('/bookings/api/payment/', { booking_id: id })
};