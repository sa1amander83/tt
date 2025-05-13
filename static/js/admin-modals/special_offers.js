document.addEventListener('DOMContentLoaded', () => {
  // Открытие модального окна с анимацией
  function openSpecialOfferModal() {
    const modal = document.getElementById('addSpecialOfferModal');
    const backdrop = document.getElementById('addSpecialOfferBackdrop');
    const content = document.getElementById('specialOfferModalContent');

    if (modal && backdrop && content) {
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      void modal.offsetWidth; // Триггер для перерисовки, чтобы сработала анимация
      backdrop.classList.add('opacity-100');
      content.classList.add('opacity-100', 'scale-100');
    }
  }

  // Закрытие модального окна с анимацией
  function closeSpecialOfferModal() {
    const modal = document.getElementById('addSpecialOfferModal');
    const backdrop = document.getElementById('addSpecialOfferBackdrop');
    const content = document.getElementById('specialOfferModalContent');

    if (modal && backdrop && content) {
      backdrop.classList.remove('opacity-100');
      content.classList.remove('opacity-100', 'scale-100');
      content.classList.add('scale-95');

      // Анимация перед скрытием
      setTimeout(() => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
      }, 300);
    }
  }

  // Сохранение спецпредложения с анимацией
  const saveSpecialOfferButton = document.getElementById('saveSpecialOffer');
  if (saveSpecialOfferButton) {
    saveSpecialOfferButton.addEventListener('click', function () {
      const form = document.getElementById('addSpecialOfferForm');
      const saveBtn = this;

      if (form.checkValidity()) {
        // Показать состояние загрузки
        saveBtn.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Сохранение...
        `;
        saveBtn.disabled = true;

        // Симуляция API вызова
        setTimeout(() => {
          // Сброс состояния кнопки
          saveBtn.innerHTML = 'Сохранить';
          saveBtn.disabled = false;

          // Закрытие модалки и уведомление об успешном сохранении
          closeSpecialOfferModal();
          showNotification('Специальное предложение успешно создано!', 'success');
        }, 1500);
      } else {
        form.reportValidity();
      }
    });
  }

  // Показать уведомление
  function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium transform translate-x-full opacity-0 transition-all duration-300 ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.remove('translate-x-full', 'opacity-0');
      notification.classList.add('translate-x-0', 'opacity-100');
    }, 50);

    setTimeout(() => {
      notification.classList.remove('translate-x-0', 'opacity-100');
      notification.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // Закрытие модалки при нажатии на кнопку
  const closeModalButton = document.getElementById('closeSpecialOfferModal');
  const cancelButton = document.getElementById('cancelSpecialOffer');
  const backdrop = document.getElementById('addSpecialOfferBackdrop');

  if (closeModalButton) {
    closeModalButton.addEventListener('click', closeSpecialOfferModal);
  }

  if (cancelButton) {
    cancelButton.addEventListener('click', closeSpecialOfferModal);
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeSpecialOfferModal);
  }

  // Переключение состояния таблицы в зависимости от чекбокса "Применить ко всем"
  const applyToAllCheckbox = document.getElementById('applyToAll');
  const tableSelection = document.getElementById('tableSelection');

  if (applyToAllCheckbox && tableSelection) {
    applyToAllCheckbox.addEventListener('change', function () {
      if (this.checked) {
        tableSelection.classList.add('opacity-50', 'pointer-events-none');
      } else {
        tableSelection.classList.remove('opacity-50', 'pointer-events-none');
      }
    });
  }
});
