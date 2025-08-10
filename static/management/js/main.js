import './bookings/cancelBooking.js';
import { initFilters } from './bookings/booking-filter.js';
import { initModals }  from './bookings/booking-modal.js';

document.addEventListener('DOMContentLoaded', () => {
  initFilters();
  initModals();
});