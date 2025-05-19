//функции для работы с ценами на типы столов

// Универсальная функция для закрытия модальных окон
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;

  // Анимация закрытия
  const backdrop = modal.querySelector('.backdrop-blur-sm');
  const content = modal.querySelector('[id$="ModalContent"]');

  if (backdrop) backdrop.classList.remove('opacity-100');
  if (content) content.classList.remove('opacity-100', 'scale-100', 'translate-y-10');

  setTimeout(() => {
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }, 300);
}

// Функции открытия для каждой модалки
function openAddPricingPlanModal() {
  const modal = document.getElementById('addPricingPlanModal');
  if (!modal) return;

  // Сброс формы и заголовка
  const form = document.getElementById('pricingPlanForm');
  if (form) form.reset();

  const title = modal.querySelector('h3');
  if (title) title.textContent = 'Новый тарифный план';

  // Показ с анимацией
  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');

  setTimeout(() => {
    const backdrop = document.getElementById('pricingPlanBackdrop');
    const content = document.getElementById('pricingPlanModalContent');
    if (backdrop) backdrop.classList.add('opacity-100');
    if (content) content.classList.add('opacity-100', 'scale-100', 'translate-y-0');
  }, 10);
}

function openAddSpecialOfferModal() {
  const modal = document.getElementById('addSpecialOfferModal');
  if (!modal) return;

  const form = document.getElementById('specialOfferForm');
  if (form) form.reset();

  const title = modal.querySelector('h3');
  if (title) title.textContent = 'Новое спецпредложение';

  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');

  setTimeout(() => {
    const backdrop = document.getElementById('specialOfferBackdrop');
    const content = document.getElementById('specialOfferModalContent');
    if (backdrop) backdrop.classList.add('opacity-100');
    if (content) content.classList.add('opacity-100', 'scale-100', 'translate-y-0');
  }, 10);



}




function openAddTableTypePricingModal() {
  const modal = document.getElementById('addTableTypePricingModal');
  if (!modal) return;

  const form = document.getElementById('tableTypePricingForm');
  if (form) form.reset();

  const title = modal.querySelector('h3');
  if (title) title.textContent = 'Цены для типа стола';

  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');

  setTimeout(() => {
    const backdrop = document.getElementById('tableTypePricingBackdrop');
    const content = document.getElementById('tableTypePricingModalContent');
    if (backdrop) backdrop.classList.add('opacity-100');
    if (content) content.classList.add('opacity-100', 'scale-100', 'translate-y-0');
  }, 10);
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function() {
  // Обработчики для кнопок открытия
  document.querySelectorAll('[data-modal="pricing-plan"]').forEach(btn => {
    btn.addEventListener('click', openAddPricingPlanModal);
  });

  document.querySelectorAll('[data-modal="special-offer"]').forEach(btn => {
    btn.addEventListener('click', openAddSpecialOfferModal);
  });

  document.querySelectorAll('[data-modal="table-type-pricing"]').forEach(btn => {
    btn.addEventListener('click', openAddTableTypePricingModal);
  });

  // Обработчики закрытия по кнопкам
  document.querySelectorAll('[onclick^="closeModal"]').forEach(btn => {
    const match = btn.getAttribute('onclick').match(/closeModal\('([^']+)'/);
    if (match && match[1]) {
      btn.addEventListener('click', () => closeModal(match[1]));
    }
  });

  // Закрытие по клику на бэкдроп
  document.querySelectorAll('.backdrop-blur-sm').forEach(backdrop => {
    backdrop.addEventListener('click', function() {
      const modal = this.closest('.fixed.inset-0');
      if (modal) closeModal(modal.id);
    });
  });
});