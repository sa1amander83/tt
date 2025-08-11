// table_pricing.js
import { $, $$ } from '../utils/dom.js';

// ==========================================================================
// Утилиты
// ==========================================================================
const csrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value;


// ==========================================================================
// Модальные окна
// ==========================================================================
const openModal = (modalId) => {
  const modal = $(`#${modalId}`);
  if (!modal) return;
  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');
};

const closeModal = (modalId) => {
  const modal = $(`#${modalId}`);
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.classList.remove('overflow-hidden');
};

// ==========================================================================
// 1. Максимальное количество неоплаченных бронирований
// ==========================================================================
const initMaxUnpaid = () => {
  const saveBtn  = $('#save_max_unpaid_bookings');
  const input    = $('#max_unpaid_bookings');
  if (!saveBtn || !input) return;

  saveBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    await fetch('/settings/set-max-unpaid-bookings/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken()
      },
      body: `max_unpaid_bookings=${encodeURIComponent(input.value)}`
    });
    showNotification('Настройки сохранены', 'success');
  });
};





const initMinTimetoCancel = () => {
  const saveBtn  = $('#save_min_time_to_cancel');
  const input    = $('#min_time_to_cancel');
  if (!saveBtn || !input) return;

  saveBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    await fetch('/settings/set-min-time-to-cancel/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken()
      },
      body: `min_time_to_cancel=${encodeURIComponent(input.value)}`
    });
    showNotification('Настройки сохранены', 'success');
  });
};










// ==========================================================================
// 2. Тарифные планы
// ==========================================================================
const deletePricingPlan = async (id) => {
  if (!confirm('Удалить тарифный план?')) return;
  await fetch(`/pricing/pricing-plans/${id}/delete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfToken() }
  });
  showNotification('Удалено', 'success');
  setTimeout(() => location.reload(), 1000);
};

// ==========================================================================
// 3. Цены для типов столов
// ==========================================================================
const saveTableTypePricing = async () => {
  const form   = $('#tableTypePricingForm');
  const saveBtn = $('#saveTableTypePricingBtn');
  if (!form || !form.checkValidity()) return form?.reportValidity();

  saveBtn.disabled = true;
  saveBtn.textContent = 'Сохранение...';

  const res = await fetch('/pricing/table-type-pricings/create/', {
    method: 'POST',
    body: new FormData(form),
    headers: { 'X-CSRFToken': csrfToken() }
  });
  const data = await res.json();

  if (res.ok) {
    showNotification('Цена сохранена', 'success');
    closeModal('addTableTypePricingModal');
    form.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    showNotification(data.message || 'Ошибка', 'error');
  }
  saveBtn.disabled = false;
  saveBtn.textContent = 'Сохранить';
};

// ==========================================================================
// 4. Специальные предложения
// ==========================================================================
const saveSpecialOffer = async () => {
  const form = $('#specialOfferForm');
  const btn  = $('#saveSpecialOfferBtn');
  if (!form || !form.checkValidity()) return form?.reportValidity();

  btn.disabled = true;
  btn.innerHTML = 'Сохранение...';

  const res = await fetch('/settings/special-offers/create/', {
    method: 'POST',
    body: new FormData(form),
    headers: { 'X-CSRFToken': csrfToken() }
  });
  const data = await res.json();

  if (res.ok) {
    showNotification('Предложение создано', 'success');
    closeModal('addSpecialOfferModal');
    form.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    showNotification(data.message || 'Ошибка', 'error');
  }
  btn.disabled = false;
  btn.innerHTML = 'Сохранить';
};

// ==========================================================================
// 5. Оборудование
// ==========================================================================
const saveEquipment = async () => {
  const form = $('#equipmentForm');
  const btn  = $('#saveEquipmentBtn');
  if (!form || !form.checkValidity()) return form?.reportValidity();

  btn.disabled = true;
  btn.innerHTML = 'Сохранение...';

  const res = await fetch('/bookings/api/equipment/', {
    method: 'POST',
    body: new FormData(form),
    headers: { 'X-CSRFToken': csrfToken() }
  });
  const data = await res.json();

  if (res.ok) {
    showNotification('Оборудование добавлено', 'success');
    closeModal('addEquipmentModal');
    form.reset();
    setTimeout(() => location.reload(), 1200);
  } else {
    showNotification(data.message || 'Ошибка', 'error');
  }
  btn.disabled = false;
  btn.innerHTML = 'Сохранить';
};

// ==========================================================================
// Инициализация
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initMaxUnpaid();
  initMinTimetoCancel();

  // кнопки «Добавить» через data-modal
  $$('[data-modal]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.dataset.modal;
      openModal(`add${modal.charAt(0).toUpperCase()}${modal.slice(1)}Modal`);
    });
  });

  // кнопки «Сохранить»
  $('#saveTableTypePricingBtn')?.addEventListener('click', saveTableTypePricing);
  $('#saveSpecialOfferBtn')?.addEventListener('click', saveSpecialOffer);
  $('#saveEquipmentBtn')?.addEventListener('click', saveEquipment);

  // кнопки «Удалить» через data-delete-*
  $$('[data-delete-pricing]').forEach(btn =>
    btn.addEventListener('click', () => deletePricingPlan(btn.dataset.deletePricing))
  );

  // закрытие модалок
  $$('[data-dismiss="modal"]').forEach(btn =>
    btn.addEventListener('click', () => closeModal(btn.closest('.modal').id))
  );
});