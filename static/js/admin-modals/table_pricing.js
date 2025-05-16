// Функции для работы с тарифными планами
function openAddPricingPlanModal() {
    const modal = document.getElementById('addPricingPlanModal');
    const backdrop = document.getElementById('pricingPlanBackdrop');
    const content = document.getElementById('pricingPlanModalContent');
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        backdrop.classList.remove('opacity-0');
        content.classList.remove('opacity-0', 'translate-y-10');
    }, 10);
}


async function deletePricingPlan(planId) {
    if (!confirm('Вы уверены, что хотите удалить этот тарифный план?')) return;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch(`/settings/pricing-plans/${planId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Ошибка сервера');
        }

        showNotification('Тарифный план успешно удален!', 'success');
        
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Error deleting pricing plan:', error);
        showNotification('Ошибка при удалении: ' + (error.message || 'Попробуйте позже'), 'error');
    }
}

// Функции для работы с ценами на типы столов
function openAddTableTypePricingModal() {
    const modal = document.getElementById('addTableTypePricingModal');
    const backdrop = document.getElementById('tableTypePricingBackdrop');
    const content = document.getElementById('tableTypePricingModalContent');
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        backdrop.classList.remove('opacity-0');
        content.classList.remove('opacity-0', 'translate-y-10');
    }, 10);
}

async function saveTableTypePricing() {
    const form = document.getElementById('tableTypePricingForm');
    const saveBtn = document.querySelector('#addTableTypePricingModal button[onclick="saveTableTypePricing()"]');

    if (form.checkValidity()) {
        try {
            saveBtn.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Сохранение...
            `;
            saveBtn.disabled = true;

            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const response = await fetch('/settings/table-type-pricings/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json',
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Ошибка сервера');
            }

            showNotification('Цены для типа стола успешно сохранены!', 'success');
            closeModal('addTableTypePricingModal');
            form.reset();
            
            setTimeout(() => {
                window.location.reload();
            }, 1500);

        } catch (error) {
            console.error('Error saving table type pricing:', error);
            showNotification('Ошибка при сохранении: ' + (error.message || 'Проверьте введенные данные'), 'error');
        } finally {
            saveBtn.innerHTML = 'Сохранить';
            saveBtn.disabled = false;
        }
    } else {
        form.reportValidity();
    }
}

// Функции для работы со специальными предложениями
function openAddSpecialOfferModal() {
    const modal = document.getElementById('addSpecialOfferModal');
    const backdrop = document.getElementById('specialOfferBackdrop');
    const content = document.getElementById('specialOfferModalContent');
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        backdrop.classList.remove('opacity-0');
        content.classList.remove('opacity-0', 'translate-y-10');
    }, 10);
}

// Общие функции
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(modalId.replace('Modal', 'Backdrop'));
    const content = document.getElementById(modalId.replace('Modal', 'ModalContent'));
    
    content.classList.add('opacity-0', 'translate-y-10');
    backdrop.classList.add('opacity-0');
    
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center transform transition-all duration-300 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    
    notification.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${
                type === 'success' ? 'M5 13l4 4L19 7' : 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            }"></path>
        </svg>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Инициализация модальных окон
document.addEventListener('DOMContentLoaded', () => {
    // Обработчики для всех кнопок с атрибутом data-modal
    document.querySelectorAll('[data-modal]').forEach(button => {
        button.addEventListener('click', (e) => {
            const modalId = `add${e.target.dataset.modal.split('-').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1))
            }.join('')}Modal`;
            
            const modal = document.getElementById(modalId);
            if (modal) {
                const backdrop = document.getElementById(modalId.replace('add', '').replace('Modal', 'Backdrop'));
                const content = document.getElementById(modalId.replace('add', '').replace('Modal', 'ModalContent'));
                
                modal.classList.remove('hidden');
                setTimeout(() => {
                    backdrop.classList.remove('opacity-0');
                    content.classList.remove('opacity-0', 'translate-y-10');
                }, 10);
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
  // Открытие модального окна с анимацией
  function openSpecialOfferModal() {
    const modal = document.getElementById('addSpecialOfferModal');
    const backdrop = document.getElementById('addSpecialOfferBackdrop');
    const content = document.getElementById('specialOfferModalContent');

    if (modal && backdrop && content) {
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      void modal.offsetWidth; // Триггер для перерисовки
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

      setTimeout(() => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
      }, 300);
    }
  }

  // Сохранение спецпредложения
  const saveSpecialOfferButton = document.getElementById('saveSpecialOffer');
  if (saveSpecialOfferButton) {
    saveSpecialOfferButton.addEventListener('click', async function () {
      const form = document.getElementById('SpecialOfferForm');
      const saveBtn = this;

      if (form.checkValidity()) {
        try {
          // Показать состояние загрузки
          saveBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Сохранение...
          `;
          saveBtn.disabled = true;

          // Подготовка данных формы
          const formData = new FormData(form);
          const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

          // Отправка данных на сервер
          const response = await fetch('/settings/special-offers/create/', {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': csrfToken,
              'Accept': 'application/json',
            }
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.message || 'Ошибка сервера');
          }

          // Успешное сохранение
          closeSpecialOfferModal();
          showNotification('Специальное предложение успешно создано!', 'success');

          // Обновление страницы через 1.5 секунды
          setTimeout(() => {
            window.location.reload();
          }, 1500);

        } catch (error) {
          console.error('Error saving special offer:', error);
          showNotification('Ошибка при сохранении: ' + (error.message || 'Проверьте введенные данные'), 'error');
        } finally {
          saveBtn.innerHTML = 'Сохранить';
          saveBtn.disabled = false;
        }
      } else {
        form.reportValidity();
      }
    });
  }

  // Функция для редактирования спецпредложения
  async function editSpecialOffer(offerId) {
    try {
      // Загрузка данных предложения
      const response = await fetch(`/settings/special-offers/${offerId}/`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Ошибка загрузки данных');
      }

      // Заполнение формы
      const form = document.getElementById('editSpecialOfferForm');
      form.querySelector('[name="name"]').value = data.name;
      form.querySelector('[name="discount_percent"]').value = data.discount_percent;
      form.querySelector('[name="valid_from"]').value = data.valid_from;
      form.querySelector('[name="valid_to"]').value = data.valid_to || '';
      form.querySelector('[name="is_active"]').checked = data.is_active;
      form.dataset.offerId = offerId;

      // Открытие модального окна
      openEditSpecialOfferModal();

    } catch (error) {
      console.error('Error loading special offer:', error);
      showNotification('Ошибка загрузки данных: ' + error.message, 'error');
    }
  }

  // Функция для обновления спецпредложения
  async function updateSpecialOffer() {
    const form = document.getElementById('editSpecialOfferForm');
    const offerId = form.dataset.offerId;
    const saveBtn = document.querySelector('#editSpecialOfferModal button[type="submit"]');

    try {
      saveBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Сохранение...
      `;
      saveBtn.disabled = true;

      const formData = new FormData(form);
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      const response = await fetch(`/settings/special-offers/${offerId}/update/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Ошибка сервера');
      }

      closeEditSpecialOfferModal();
      showNotification('Специальное предложение успешно обновлено!', 'success');

      setTimeout(() => {
        window.location.reload();
      }, 1500);

    } catch (error) {
      console.error('Error updating special offer:', error);
      showNotification('Ошибка при обновлении: ' + (error.message || 'Проверьте введенные данные'), 'error');
    } finally {
      saveBtn.innerHTML = 'Сохранить';
      saveBtn.disabled = false;
    }
  }

  // Функция для удаления спецпредложения
  async function deleteSpecialOffer(offerId) {
    if (!confirm('Вы уверены, что хотите удалить это специальное предложение?')) return;

    try {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      const response = await fetch(`/settings/special-offers/${offerId}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Ошибка сервера');
      }

      showNotification('Специальное предложение успешно удалено!', 'success');

      setTimeout(() => {
        window.location.reload();
      }, 1000);

    } catch (error) {
      console.error('Error deleting special offer:', error);
      showNotification('Ошибка при удалении: ' + (error.message || 'Попробуйте позже'), 'error');
    }
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

  // Закрытие модалки
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

  // Переключение состояния таблицы
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

  // Обработчики для кнопок редактирования и удаления
  document.querySelectorAll('[data-edit-offer]').forEach(button => {
    button.addEventListener('click', () => editSpecialOffer(button.dataset.editOffer));
  });

  document.querySelectorAll('[data-delete-offer]').forEach(button => {
    button.addEventListener('click', () => deleteSpecialOffer(button.dataset.deleteOffer));
  });
});