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
function openEditPricingPlanModal(planId) {
  // Загружаем данные тарифного плана (заглушка)
  const planData = {
    id: planId,
    name: `Тариф ${planId}`,
    description: `Описание тарифа ${planId}`,
    valid_from: '2023-01-01',
    valid_to: '2023-12-31',
    is_default: planId === 1
  };

  // Заполняем форму данными
  const form = document.getElementById('PricingPlanForm');
  form.reset();

  document.getElementById('planName').value = planData.name;
  document.getElementById('planDescription').value = planData.description;
  document.getElementById('validFrom').value = planData.valid_from;
  document.getElementById('validTo').value = planData.valid_to;
  document.getElementById('isDefault').checked = planData.is_default;

  // Показываем модальное окно
  openModal('addPricingPlanModal');

  // Меняем заголовок для режима редактирования
  document.querySelector('#addPricingPlanModal h3').textContent = 'Редактировать тарифный план';
}

// ==============================================
// Функции для модального окна Table Type Pricing
// ==============================================

/**
 * Открытие модального окна для редактирования Table Type Pricing
 */
function openEditTableTypePricingModal(pricingId) {
  // Загружаем данные ценообразования (заглушка)
  const pricingData = {
    id: pricingId,
    table_type: pricingId % 3 + 1,
    pricing_plan: pricingId % 2 + 1,
    hour_rate: 400 + (pricingId * 50),
    hour_rate_group: 600 + (pricingId * 50),
    min_duration: 1,
    max_duration: 3
  };

  // Заполняем форму данными
  const form = document.getElementById('TableTypePricingForm');
  form.reset();

  document.getElementById('tableType').value = pricingData.table_type;
  document.getElementById('pricingPlan').value = pricingData.pricing_plan;
  document.getElementById('hourRate').value = pricingData.hour_rate;
  document.getElementById('hourRateGroup').value = pricingData.hour_rate_group;
  document.getElementById('minDuration').value = pricingData.min_duration;
  document.getElementById('maxDuration').value = pricingData.max_duration;

  // Показываем модальное окно
  openModal('addTableTypePricingModal');

  // Меняем заголовок для режима редактирования
  document.querySelector('#addTableTypePricingModal h3').textContent = 'Редактировать цены';
}

// ==============================================
// Функции для модального окна Membership
// ==============================================

/**
 * Открытие модального окна для редактирования Membership
 */
function openEditMembershipModal(membershipId) {
  // Загружаем данные абонемента (заглушка)
  const membershipData = {
    id: membershipId,
    name: `Абонемент ${membershipId}`,
    description: `Описание абонемента ${membershipId}`,
    duration_days: 30 * membershipId,
    price: 1000 * membershipId,
    is_active: true
  };

  // Находим форму (предполагаем, что она аналогична форме добавления)
  const form = document.getElementById('add-membership-modal').querySelector('form');
  form.reset();

  // Заполняем поля (имена полей должны соответствовать вашей форме)
  form.querySelector('[name="name"]').value = membershipData.name;
  form.querySelector('[name="description"]').value = membershipData.description;
  form.querySelector('[name="duration_days"]').value = membershipData.duration_days;
  form.querySelector('[name="price"]').value = membershipData.price;
  form.querySelector('[name="is_active"]').checked = membershipData.is_active;

  // Показываем модальное окно
  document.getElementById('add-membership-modal').classList.remove('hidden');

  // Меняем заголовок для режима редактирования
  document.querySelector('#add-membership-modal h3').textContent = 'Редактировать абонемент';
}

// ==============================================
// Универсальные функции для работы с модальными окнами
// ==============================================

/**
 * Универсальная функция открытия модального окна
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  const backdrop = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}Backdrop`);
  const content = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}ModalContent`);

  if (!modal) return;

  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');

  // Анимация открытия
  setTimeout(() => {
    if (backdrop) backdrop.classList.add('opacity-100');
    if (content) content.classList.add('opacity-100', 'scale-100');
  }, 10);
}

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
