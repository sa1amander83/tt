/* static/js/management/booking-filters.js */


import {fetchBookings} from "./booking-fetch.js";

export function initFilters() {
  // flatpickr – date only
  flatpickr('#apply-date-filter', {
    dateFormat: 'Y-m-d',
    locale: 'ru',
    static: true,
    enableTime: false,
  });

  // status buttons
  document.querySelectorAll('.status-button').forEach(btn =>
    btn.addEventListener('click', () => {
      document.getElementById('filter-status').value = btn.dataset.status;

      // active styling
      document.querySelectorAll('.status-button').forEach(b => {
        b.classList.remove('bg-green-500', 'text-white');
        b.classList.add('bg-gray-200');
      });
      btn.classList.remove('bg-gray-200');
      btn.classList.add('bg-green-500', 'text-white');

      fetchBookings();
    })
  );

  // auto-apply when date changes
  document
    .getElementById('apply-date-filter')
    ?.addEventListener('change', fetchBookings);
}