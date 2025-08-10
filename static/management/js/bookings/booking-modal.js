/* static/js/management/booking-modals.js */


import { fetchBookings }     from './booking-fetch.js';

export function initModals() {
  // date/time pickers inside modals
  document.querySelectorAll('[data-datepicker]').forEach(el =>
    flatpickr(el, {
      enableTime: true,
      dateFormat: 'Y-m-d H:i',
      locale: 'ru',
      time_24hr: true,
      minuteIncrement: 15,
      static: true,
    })
  );

  document.querySelectorAll('[data-timepicker]').forEach(el =>
    flatpickr(el, {
      enableTime: true,
      noCalendar: true,
      dateFormat: 'H:i',
      locale: 'ru',
      time_24hr: true,
      minuteIncrement: 15,
    })
  );

  // form submissions
  document.querySelectorAll('.modal-form').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const original = btn.textContent;
      btn.disabled = true;
      btn.innerHTML =
        '<span class="inline-block animate-spin mr-2">↻</span> Обработка...';

      try {
        const res = await fetch(form.action, {
          method: form.method,
          body: new FormData(form),
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken(),
          },
        });
        const data = await res.json();
        if (data.success) {
          window.location.reload(); // or close modal + fetchBookings()
        } else {
          const box = form.querySelector('.form-errors');
          if (box) {
            box.classList.remove('hidden');
            box.innerHTML =
              Object.values(data.errors || {})
                .flat()
                .map(e => `<p class="text-red-500 text-sm">${e}</p>`)
                .join('') || '<p class="text-red-500 text-sm">Ошибка</p>';
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        btn.disabled = false;
        btn.textContent = original;
      }
    });
  });

  // delegated ESC / overlay close
  document.addEventListener('keydown', escClose);
  document.addEventListener('click', overlayClose);
}

// helpers
function escClose(e) {
  if (e.key === 'Escape') {
    const open = document.querySelector('.modal:not(.hidden)');
    if (open) closeModal(open.id);
  }
}
function overlayClose(e) {
  if (e.target.classList.contains('modal-overlay')) {
    const modal = e.target.closest('.modal');
    if (modal) closeModal(modal.id);
  }
}

// global helpers (used by inline onclick="...")
window.openModal  = id => {
  const m = document.getElementById(id);
  m?.classList.remove('hidden');
  m?.classList.add('flex');
  document.body.style.overflow = 'hidden';
};
window.closeModal = id => {
  const m = document.getElementById(id);
  m?.classList.add('hidden');
  m?.classList.remove('flex');
  document.body.style.overflow = 'auto';
};


