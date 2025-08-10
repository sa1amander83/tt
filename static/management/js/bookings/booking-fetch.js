/* static/js/management/booking-fetch.js */
export function fetchBookings() {
  const form = document.getElementById('booking-filters-form');
  if (!form) return;

  const params = new URLSearchParams(new FormData(form)).toString();
  const baseUrl = document.getElementById('filter-button')?.dataset?.url;
  const url = `${baseUrl}?${params}`;

  fetch(url, {
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
  })
    .then(r => {
      if (!r.ok) throw new Error('Сетевая ошибка');
      return r.json();
    })
    .then(data => {
      const container = document.getElementById('bookings-container');
      if (container) container.innerHTML = data.html;
    })
    .catch(err => {
      console.error(err);
      alert('Ошибка загрузки бронирований.');
    });
}

// delegated pagination clicks
document.addEventListener('click', e => {
  const link = e.target.closest('.pagination a');
  if (!link) return;
  e.preventDefault();

  fetch(link.href, {
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
  })
    .then(r => {
      if (!r.ok) throw new Error('Сетевая ошибка');
      return r.json();
    })
    .then(data => {
      const container = document.getElementById('bookings-container');
      if (container) container.innerHTML = data.html;
    })
    .catch(() => alert('Ошибка загрузки бронирований.'));
});