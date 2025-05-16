document.addEventListener('DOMContentLoaded', () => {
  // Открытие модального окна с анимацией

  // Закрытие модального окна с анимацией

  // Сохранение спецпредложения с анимацией
  const saveSpecialOfferButton = document.getElementById('saveSpecialOffer');
  if (saveSpecialOfferButton) {
    saveSpecialOfferButton.addEventListener('click', function () {
      const form = document.getElementById('SpecialOfferForm');
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

  // Закрытие модалки при нажатии на кнопку


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
