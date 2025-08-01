// Функции для работы с тарифными планами
import {getCSRFToken} from "../utils.js";

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


document.addEventListener('DOMContentLoaded', function() {
    // Получаем текущее значение с сервера
    fetch('/settings/get-max-unpaid-bookings/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('max_unpaid_bookings').value = data.max_unpaid_bookings;
        });

    document.getElementById('save_max_unpaid_bookings').addEventListener('click', function(e) {
        e.preventDefault();
        const value = document.getElementById('max_unpaid_bookings').value;

        fetch("/settings/set-max-unpaid-bookings/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken(), // если используете csrf_token
            },
            body: `max_unpaid_bookings=${encodeURIComponent(value)}`
        })
        .then(response => response.json())
        .then(data => {
           showNotification('Настройки сохранены!', 'success');
        })
        .catch(error => {
            alert("Ошибка: " + error);
        });
    });
});








async function deletePricingPlan(planId) {
    if (!confirm('Вы уверены, что хотите удалить этот тарифный план?')) return;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch(`/pricing/pricing-plans/${planId}/delete/`, {
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
    const saveBtn = document.getElementById('save_button_table_price');

    if (form.checkValidity()) {
        try {
            saveBtn.innerHTML = ` <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>   `;
            saveBtn.disabled = true;

            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const response = await fetch('/pricing/table-type-pricings/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                }
            });

            const data = await response.json();

            if (!response.ok) {
                // Показываем конкретные ошибки валидации
                if (data.errors) {
                    let errorMessages = [];
                    for (const [field, errors] of Object.entries(data.errors)) {
                        errorMessages.push(`${field}: ${errors.join(', ')}`);
                    }
                    throw new Error(errorMessages.join('\n'));
                }
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
            showNotification('Ошибка при сохранении: ' + error.message, 'error');
        } finally {
            saveBtn.innerHTML = 'Сохранить';
            saveBtn.disabled = false;
        }
    } else {
        form.reportValidity();
    }
}




// ==============================================
// Функции для работы с Table Type Pricing
// ==============================================

/**
 * Сохранение цен для типа стола
 */


/**
 * Удаление цены для типа стола
 */

// ==============================================
// Функции для работы с Special Offers
// ==============================================

/**
 * Сохранение специального предложения
 */

/**
 * Удаление специального предложения
 */


// ==============================================
// Общие вспомогательные функции
// ==============================================

/**
 * Универсальная функция открытия модального окна с анимацией
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;

  const backdrop = modal.querySelector('.backdrop-blur-sm');
  const content = modal.querySelector('[id$="ModalContent"]');

  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');

  setTimeout(() => {
    backdrop.classList.remove('opacity-0');
    backdrop.classList.add('opacity-100');
    content.classList.remove('opacity-0', 'translate-y-10');
    content.classList.add('opacity-100', 'translate-y-0');
  }, 10);
}

/**
 * Инициализация обработчиков для кнопок действий в таблицах
 */
function initTableActionHandlers() {
  // Обработчики для кнопок редактирования Table Type Pricing
  document.querySelectorAll('[onclick^="openEditTableTypePricingModal"]').forEach(btn => {
    const match = btn.getAttribute('onclick').match(/openEditTableTypePricingModal\((\d+)\)/);
    if (match) {
      btn.addEventListener('click', () => openEditTableTypePricingModal(match[1]));
    }
  });

}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  initTableActionHandlers();

  // Обработчики для кнопок сохранения в формах
  document.getElementById('saveTableTypePricingBtn')?.addEventListener('click', saveTableTypePricing);
  document.getElementById('saveSpecialOfferBtn')?.addEventListener('click', saveSpecialOffer);

  // Обработчики для кнопок закрытия модальных окон
  document.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', function() {
      const modal = this.closest('.modal');
      if (modal) {
        closeModal(modal.id);
      }
    });
  });
});



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
    const backdrop = document.getElementById('specialOfferBackdrop');
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
    const backdrop = document.getElementById('specialOfferBackdrop');
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
/**
  // Сохранение спецпредложения
  const saveSpecialOfferButton = document.getElementById('SaveSpecialOffer');
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
**/
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

      const response = await fetch(`/management/special-offers/${offerId}/update/`, {
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

  // Показать уведомление

  // Закрытие модалки
  const closeModalButton = document.getElementById('closeSpecialOfferModal');
  const cancelButton = document.getElementById('cancelSpecialOffer');
  const backdrop = document.getElementById('specialOfferBackdrop');

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


});

// Функция для открытия модального окна редактирования типа стола
function openEditTableTypeModal(tableTypeId) {
    fetch(`/settings/table-types/${tableTypeId}/`)
        .then(response => response.json())
        .then(data => {
            // Заполняем форму данными
            document.getElementById('editTableTypeId').value = data.id;
            document.getElementById('editTableTypeName').value = data.name;
            document.getElementById('editTableTypeDescription').value = data.description;
            document.getElementById('editTableTypeCapacity').value = data.max_capacity;

            // Показываем модальное окно
            document.getElementById('edit-table-type-modal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Ошибка загрузки данных типа стола', 'error');
        });
}

// Функция для сохранения изменений типа стола
function saveTableType() {
    const form = document.getElementById('editTableTypeForm');
    const tableTypeId = form.elements['id'].value;
    const saveBtn = document.getElementById('saveTableTypeBtn');

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Сохранение...';

    fetch(`/settings/table-types/${tableTypeId}/update/`, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.message || 'Ошибка сервера');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Сохранить';
    });
}



// Функция для открытия модального окна редактирования стола
function openEditTableModal(tableId) {
    // Получаем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Показываем индикатор загрузки
    const editBtn = document.querySelector(`button[onclick="openEditTableModal(${tableId})"]`);
    const originalText = editBtn.innerHTML;
    editBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    editBtn.disabled = true;

    // Получаем данные стола через AJAX
    fetch(`/settings/tables/${tableId}/`, {
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        return response.json();
    })
    .then(data => {
        // Заполняем форму данными
        document.getElementById('editTableId').value = data.id;
        document.getElementById('editTableNumber').value = data.number;
        document.getElementById('editTableType').value = data.table_type.id;
        document.getElementById('editTableDescription').value = data.description;
        document.getElementById('editTableIsActive').checked = data.is_active;

        // Показываем модальное окно
        document.getElementById('edit-table-modal').classList.remove('hidden');
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка загрузки данных стола: ' + error.message, 'error');
    })
    .finally(() => {
        editBtn.innerHTML = originalText;
        editBtn.disabled = false;
    });
}

// Функция для сохранения изменений стола
function saveTableChanges() {
    const form = document.getElementById('editTableForm');
    const tableId = form.elements['id'].value;
    const saveBtn = document.getElementById('saveTableBtn');

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Сохранение...';

    fetch(`/settings/tables/${tableId}/update/`, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Стол успешно обновлен', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.message || 'Ошибка сервера');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении стола: ' + error.message, 'error');
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Сохранить';
          document.getElementById('edit-table-modal').classList.add('hidden');

    });
}




// Функция для удаления типа стола
function deleteTableType(tableTypeId) {
    if (!confirm('Вы уверены, что хотите удалить этот тип стола? Все связанные столы будут переведены в тип по умолчанию.')) {
        return;
    }

    fetch(`/settings/table-types/${tableTypeId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.message || 'Ошибка сервера');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    });
}