// ==============================================
// Функции для модального окна Special Offer
// ==============================================

/**
 * Закрытие модального окна Special Offer
 */
function closeSpecialOfferModal() {
  const modal = document.getElementById('addSpecialOfferModal');
  const backdrop = document.getElementById('addSpecialOfferBackdrop');
  const content = document.getElementById('specialOfferModalContent');

  // Анимация закрытия
  backdrop.classList.remove('opacity-100');
  content.classList.remove('opacity-100', 'scale-100');

  setTimeout(() => {
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }, 300);
}

/**
 * Открытие модального окна для редактирования Special Offer
 **/


function openEditSpecialOfferModal(offerId) {
  // Загружаем данные предложения (заглушка - в реальном коде будет AJAX запрос)
  const offerData = {
    id: offerId,
    name: `Акция ${offerId}`,
    discount_percent: 15,
    valid_from: '2023-06-01',
    valid_to: '2023-06-30',
    is_active: true,
    time_from: '14:00',
    time_to: '18:00'
  };

  // Заполняем форму данными
  const form = document.getElementById('SpecialOfferForm');
  form.reset();

  document.getElementById('offerName').value = offerData.name;
  document.getElementById('discountPercent').value = offerData.discount_percent;
  document.getElementById('validFrom').value = offerData.valid_from;
  document.getElementById('validTo').value = offerData.valid_to;
  document.getElementById('isActive').checked = offerData.is_active;
  document.getElementById('timeFrom').value = offerData.time_from;
  document.getElementById('timeTo').value = offerData.time_to;

  // Показываем модальное окно
  openModal('addSpecialOfferModal');

  // Меняем заголовок для режима редактирования
  document.querySelector('#addSpecialOfferModal h3').textContent = 'Редактировать предложение';
}

// ==============================================
// Функции для модального окна Pricing Plan
// ==============================================

/**
 * Открытие модального окна для редактирования Pricing Plan
 */
// ==============================================
// Функции для модального окна Pricing Plan
// ==============================================

/**
 * Открытие модального окна для редактирования Pricing Plan
 */
async function openEditPricingPlanModal(planId) {
  try {
    const modal = document.getElementById('addPricingPlanModal');
    const form = document.getElementById('pricingPlanForm');

    // Проверяем, что элементы существуют
    if (!modal || !form) {
      throw new Error('Modal or form element not found');
    }

    // Показываем модальное окно сразу
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    // Добавляем индикатор загрузки внутрь формы
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'text-center py-4';
    loadingIndicator.innerHTML = `
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      <p class="mt-2 text-gray-600">Загрузка данных...</p>
    `;

    // Сохраняем оригинальное содержимое формы
    const originalContent = form.innerHTML;

    // Заменяем содержимое формы индикатором загрузки
    form.innerHTML = '';
    form.appendChild(loadingIndicator);

    // Загружаем данные тарифного плана с сервера
    const response = await fetch(`/settings/pricing-plans/${planId}/`);
    if (!response.ok) {
      throw new Error('Не удалось загрузить данные тарифа');
    }
    const planData = await response.json();

    // Восстанавливаем оригинальное содержимое формы
    form.innerHTML = originalContent;

    // Заполняем форму данными
    form.querySelector('[name="name"]').value = planData.name || '';
    form.querySelector('[name="valid_from"]').value = planData.valid_from || '';
    form.querySelector('[name="valid_to"]').value = planData.valid_to || '';
    form.querySelector('[name="is_default"]').checked = Boolean(planData.is_default);
    form.dataset.planId = planId;

    // Меняем заголовок для режима редактирования
    const modalTitle = modal.querySelector('h3');
    if (modalTitle) {
      modalTitle.textContent = 'Редактировать тарифный план';
    }

  } catch (error) {
    console.error('Ошибка загрузки тарифного плана:', error);

    // Закрываем модальное окно при ошибке
    const modal = document.getElementById('addPricingPlanModal');
    if (modal) {
      modal.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }

    showNotification(`Ошибка: ${error.message}`, 'error');
  }
}
/**
 * Обновление тарифного плана
 */
async function updatePricingPlan() {
  const form = document.getElementById('pricingPlanForm');
  const planId = form.dataset.planId;
  const saveBtn = form.querySelector('button[type="submit"]');

  if (form.checkValidity()) {
    try {
      // Показать состояние загрузки
      saveBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Сохранение...
      `;
      saveBtn.disabled = true;

      // Подготовка данных формы
      const formData = new FormData(form);
      formData.append('is_default', form.querySelector('[name="is_default"]').checked ? 'true' : 'false');

      // Отправка данных на сервер
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const response = await fetch(`/settings/pricing-plans/${planId}/update/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка сервера');
      }

      showNotification('Тарифный план успешно обновлен!', 'success');
      closeModal('addPricingPlanModal');

      // Обновляем страницу через 1.5 секунды
      setTimeout(() => {
        window.location.reload();
      }, 1500);

    } catch (error) {
      console.error('Ошибка обновления тарифа:', error);
      showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
      saveBtn.innerHTML = 'Сохранить';
      saveBtn.disabled = false;
    }
  } else {
    form.reportValidity();
  }
}

// ==============================================
// Функции для модального окна Table Type Pricing
// ==============================================

/**
 * Открытие модального окна для редактирования Table Type Pricing
 */
async function openEditTableTypePricingModal(pricingId) {
  try {
    // Показываем индикатор загрузки
    const modal = document.getElementById('addTableTypePricingModal');
    modal.querySelector('.modal-content').innerHTML = `
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    `;
    openModal('addTableTypePricingModal');

    // Загружаем данные ценообразования с сервера
    const response = await fetch(`/settings/table-type-pricings/${pricingId}/`);
    if (!response.ok) {
      throw new Error('Не удалось загрузить данные ценообразования');
    }
    const pricingData = await response.json();

    // Заполняем форму данными
    const form = document.getElementById('tableTypePricingForm');
    form.reset();

    form.querySelector('[name="table_type"]').value = pricingData.table_type.id;
    form.querySelector('[name="pricing_plan"]').value = pricingData.pricing_plan.id;
    form.querySelector('[name="hour_rate"]').value = pricingData.hour_rate;
    form.querySelector('[name="hour_rate_group"]').value = pricingData.hour_rate_group;
    form.querySelector('[name="min_duration"]').value = pricingData.min_duration;
    form.querySelector('[name="max_duration"]').value = pricingData.max_duration;
    form.dataset.pricingId = pricingId;

    // Восстанавливаем содержимое модального окна
    modal.querySelector('.modal-content').innerHTML = `
      <!-- Ваш HTML-код модального окна -->
      <div class="modal-header">
        <h3>Редактировать цены</h3>
        <button onclick="closeModal('addTableTypePricingModal')">×</button>
      </div>
      <div class="modal-body">
        <form id="tableTypePricingForm">
          <!-- Поля формы -->
        </form>
      </div>
      <div class="modal-footer">
        <button onclick="updateTableTypePricing()">Сохранить</button>
      </div>
    `;

  } catch (error) {
    console.error('Ошибка загрузки ценообразования:', error);
    closeModal('addTableTypePricingModal');
    showNotification(`Ошибка: ${error.message}`, 'error');
  }
}

/**
 * Обновление ценообразования для типа стола
 */
async function updateTableTypePricing() {
  const form = document.getElementById('tableTypePricingForm');
  const pricingId = form.dataset.pricingId;
  const saveBtn = form.querySelector('button[type="submit"]');

  if (form.checkValidity()) {
    try {
      // Показать состояние загрузки
      saveBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Сохранение...
      `;
      saveBtn.disabled = true;

      // Подготовка данных формы
      const formData = new FormData(form);

      // Отправка данных на сервер
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const response = await fetch(`/settings/table-type-pricings/${pricingId}/update/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка сервера');
      }

      showNotification('Цены успешно обновлены!', 'success');
      closeModal('addTableTypePricingModal');

      // Обновляем страницу через 1.5 секунды
      setTimeout(() => {
        window.location.reload();
      }, 1500);

    } catch (error) {
      console.error('Ошибка обновления цен:', error);
      showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
      saveBtn.innerHTML = 'Сохранить';
      saveBtn.disabled = false;
    }
  } else {
    form.reportValidity();
  }
}

// ==============================================
// Функции для модального окна Membership
// ==============================================

/**
 * Открытие модального окна для редактирования Membership
 */
async function openEditMembershipModal(membershipId) {
  try {
    // Показываем индикатор загрузки
    const modal = document.getElementById('addMembershipModal');
    modal.querySelector('.modal-content').innerHTML = `
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    `;
    openModal('addMembershipModal');

    // Загружаем данные абонемента с сервера
    const response = await fetch(`/settings/memberships/${membershipId}/`);
    if (!response.ok) {
      throw new Error('Не удалось загрузить данные абонемента');
    }
    const membershipData = await response.json();

    // Заполняем форму данными
    const form = document.getElementById('membershipForm');
    form.reset();

    form.querySelector('[name="name"]').value = membershipData.name;
    form.querySelector('[name="description"]').value = membershipData.description;
    form.querySelector('[name="duration_days"]').value = membershipData.duration_days;
    form.querySelector('[name="price"]').value = membershipData.price;
    form.querySelector('[name="is_active"]').checked = membershipData.is_active;
    form.dataset.membershipId = membershipId;

    // Восстанавливаем содержимое модального окна
    modal.querySelector('.modal-content').innerHTML = `
      <!-- Ваш HTML-код модального окна -->
      <div class="modal-header">
        <h3>Редактировать абонемент</h3>
        <button onclick="closeModal('addMembershipModal')">×</button>
      </div>
      <div class="modal-body">
        <form id="membershipForm">
          <!-- Поля формы -->
        </form>
      </div>
      <div class="modal-footer">
        <button onclick="updateMembership()">Сохранить</button>
      </div>
    `;

  } catch (error) {
    console.error('Ошибка загрузки абонемента:', error);
    closeModal('addMembershipModal');
    showNotification(`Ошибка: ${error.message}`, 'error');
  }
}

/**
 * Обновление абонемента
 */
async function updateMembership() {
  const form = document.getElementById('membershipForm');
  const membershipId = form.dataset.membershipId;
  const saveBtn = form.querySelector('button[type="submit"]');

  if (form.checkValidity()) {
    try {
      // Показать состояние загрузки
      saveBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Сохранение...
      `;
      saveBtn.disabled = true;

      // Подготовка данных формы
      const formData = new FormData(form);

      // Отправка данных на сервер
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const response = await fetch(`/settings/memberships/${membershipId}/update/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка сервера');
      }

      showNotification('Абонемент успешно обновлен!', 'success');
      closeModal('addMembershipModal');

      // Обновляем страницу через 1.5 секунды
      setTimeout(() => {
        window.location.reload();
      }, 1500);

    } catch (error) {
      console.error('Ошибка обновления абонемента:', error);
      showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
      saveBtn.innerHTML = 'Сохранить';
      saveBtn.disabled = false;
    }
  } else {
    form.reportValidity();
  }
}

// Вспомогательные функции
function openModal(modalId) {
  document.getElementById(modalId).classList.remove('hidden');
  document.body.classList.add('overflow-hidden');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  document.body.classList.remove('overflow-hidden');
}

function showNotification(message, type) {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded shadow-lg text-white ${
    type === 'success' ? 'bg-green-500' : 'bg-red-500'
  }`;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// ==============================================
// Универсальные функции для работы с модальными окнами
// ==============================================

/**
 * Универсальная функция открытия модального окна
 */

// Инициализация всех обработчиков при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  // Обработчики для Special Offer Modal
  document.getElementById('closeSpecialOfferModal')?.addEventListener('click', closeSpecialOfferModal);
  document.getElementById('cancelSpecialOffer')?.addEventListener('click', closeSpecialOfferModal);
  document.getElementById('addSpecialOfferBackdrop')?.addEventListener('click', closeSpecialOfferModal);

  // Можно добавить аналогичные обработчики для других модальных окон
  // или использовать универсальный подход из initModals()
});

// Вспомогательная функция для показа уведомлений
