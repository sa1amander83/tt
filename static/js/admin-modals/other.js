//   другие функции для всякого говна Функции для модального окна Special Offer
// ==============================================

/**
 * Закрытие модального окна Special Offer
 */
function closeSpecialOfferModal() {
    const modal = document.getElementById('addSpecialOfferModal');
    const backdrop = document.getElementById('specialOfferBackdrop');
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

/**
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
 **/
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

        if (!modal || !form) {
            throw new Error('Modal or form not found');
        }

        // Показываем модальное окно с индикатором загрузки
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');

        // Добавляем индикатор загрузки
        const loader = document.createElement('div');
        loader.className = 'absolute inset-0 flex items-center justify-center bg-white bg-opacity-80';
        loader.innerHTML = '<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>';
        form.appendChild(loader);

        // Получаем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Загружаем данные тарифного плана
        const response = await fetch(`/settings/pricing-plans/${planId}/`, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load pricing plan');
        }

        const planData = await response.json();

        // Убираем индикатор загрузки
        form.removeChild(loader);

        // Заполняем форму данными
        form.querySelector('[name="name"]').value = planData.name || '';
        form.querySelector('[name="valid_from"]').value = planData.valid_from || '';
        form.querySelector('[name="valid_to"]').value = planData.valid_to || '';
        form.querySelector('[name="is_default"]').checked = planData.is_default || false;

        // Добавляем ID плана в форму
        if (!form.dataset.planId) {
            form.dataset.planId = planId;
        }

        // Меняем заголовок
        const title = modal.querySelector('h3');
        if (title) {
            title.textContent = 'Редактировать тарифный план';
        }

        // Анимация появления
        setTimeout(() => {
            const backdrop = document.getElementById('pricingPlanBackdrop');
            const content = document.getElementById('pricingPlanModalContent');
            if (backdrop) backdrop.classList.add('opacity-100');
            if (content) content.classList.add('opacity-100', 'translate-y-0');
        }, 10);

    } catch (error) {
        console.error('Error loading pricing plan:', error);
        closeModal('addPricingPlanModal');
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

/**
 * Сохранение тарифного плана (работает и для создания и для редактирования)
 */
async function savePricingPlan() {
    const form = document.getElementById('pricingPlanForm');
    const planId = form.dataset.planId;
    const isEditMode = !!planId;
    const saveBtn = document.getElementById('save_price_plan_button');

    try {
        // Показать состояние загрузки
        saveBtn.innerHTML = `
      <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" role="status"></span>
      Сохранение...
    `;
        saveBtn.disabled = true;

        // Подготовка данных
        const formData = new FormData(form);
        formData.append('is_default', form.querySelector('[name="is_default"]').checked ? 'true' : 'false');

        // Определяем URL и метод
        const url = isEditMode
            ? `/settings/pricing-plans/${planId}/update/`
            : '/settings/pricing-plans/create/';
        const method = 'POST';

        // Получаем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Отправляем запрос
        const response = await fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Ошибка сервера');
        }

        showNotification(
            isEditMode
                ? 'Тарифный план успешно обновлен!'
                : 'Тарифный план успешно создан!',
            'success'
        );

        closeModal('addPricingPlanModal');

        // Обновляем страницу через 1 секунду
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Error saving pricing plan:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        saveBtn.innerHTML = 'Сохранить';
        saveBtn.disabled = false;
    }
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function () {
    // Обработчик для кнопок редактирования в таблице
    document.querySelectorAll('[onclick^="openEditPricingPlanModal"]').forEach(btn => {
        const match = btn.getAttribute('onclick').match(/openEditPricingPlanModal\((\d+)\)/);
        if (match) {
            btn.addEventListener('click', () => openEditPricingPlanModal(match[1]));
        }
    });

    // Обработчик для кнопки сохранения
    const saveBtn = document.querySelector('#pricingPlanForm button[type="submit"]');
    if (saveBtn) {
        saveBtn.addEventListener('click', savePricingPlan);
    }
});

// ==============================================
// Функции для модального окна Table Type Pricing
// ==============================================

/**
 * Открытие модального окна для редактирования Table Type Pricing
 */
// Открытие модального окна для редактирования
async function openEditTableTypePricingModal(pricingId) {
    try {
        const modal = document.getElementById('addTableTypePricingModal');
        const modalBody = document.getElementById('modalBody');
        const modalTitle = document.getElementById('modalTitle');
        const modalFooter = document.getElementById('modalFooter');
        const saveButton = document.getElementById('saveButton');

        // Показать индикатор загрузки
        modalBody.innerHTML = `
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        `;

        openModal('addTableTypePricingModal');

        // Загрузить данные с сервера
        const response = await fetch(`/settings/table-type-pricings/${pricingId}/`);
        if (!response.ok) throw new Error('Не удалось загрузить данные');
        const pricingData = await response.json();

        // Заполнить форму
        const formHtml = `
            <form id="tableTypePricingForm" class="space-y-3">
                {% csrf_token %}
                <input type="hidden" name="pricing_id" value="${pricingId}">
                
                <div class="space-y-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Тип стола*</label>
                        <select name="table_type" required
                                class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                            <option value="">Выберите тип</option>
                            {% for table_type in table_types %}
                            <option value="{{ table_type.id }}" ${pricingData.table_type.id === {{ table_type.id }} ? 'selected' : ''}>
                                {{ table_type.name }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Тарифный план*</label>
                        <select name="pricing_plan" required
                                class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                            <option value="">Выберите тариф</option>
                            {% for plan in pricing_plans %}
                            <option value="{{ plan.id }}" ${pricingData.pricing_plan.id === {{ plan.id }} ? 'selected' : ''}>
                                {{ plan.name }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                
                <div class="space-y-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Цена за час (₽)*</label>
                        <input type="number" name="hour_rate" required min="0" value="${pricingData.hour_rate}"
                               class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Групповая цена (₽)*</label>
                        <input type="number" name="hour_rate_group" required min="0" value="${pricingData.hour_rate_group}"
                               class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                    </div>
                </div>

                <div class="space-y-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Минимальное время игры (мин)*</label>
                        <input type="number" name="min_duration" required min="0" value="${pricingData.min_duration}"
                               class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Максимальное время игры (мин)*</label>
                        <input type="number" name="max_duration" required min="0" value="${pricingData.max_duration}"
                               class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                    </div>
                </div>

                <div class="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-lg text-xs">
                    <div class="flex items-start">
                        <svg class="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        </svg>
                        <p class="ml-2 text-yellow-700">
                            Убедитесь, что такая комбинация типа стола и тарифа еще не существует
                        </p>
                    </div>
                </div>
            </form>
        `;

        modalBody.innerHTML = formHtml;
        modalTitle.textContent = 'Редактировать цены для типа стола';

        // Обновить обработчик сохранения
        saveButton.onclick = () => updateTableTypePricing(pricingId);

    } catch (error) {
        console.error('Ошибка загрузки ценообразования:', error);
        closeModal('addTableTypePricingModal');
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

// Сохранение новой цены
async function saveTableTypePricing() {
    const form = document.getElementById('tableTypePricingForm');
    const saveButton = document.getElementById('saveButton');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        // Показать состояние загрузки
        saveButton.innerHTML = `
            <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" role="status"></span>
            Сохранение...
        `;
        saveButton.disabled = true;

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch('/settings/table-type-pricings/create/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка сервера');
        }

        showNotification('Цены успешно сохранены!', 'success');
        closeModal('addTableTypePricingModal');

        // Обновить страницу через 1 секунду
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Ошибка сохранения цен:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        saveButton.innerHTML = 'Сохранить';
        saveButton.disabled = false;
    }
}

// Обновление существующей цены
async function updateTableTypePricing(pricingId) {
    const form = document.getElementById('tableTypePricingForm');
    const saveButton = document.getElementById('saveButton');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        // Показать состояние загрузки
        saveButton.innerHTML = `
            <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" role="status"></span>
            Сохранение...
        `;
        saveButton.disabled = true;

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch(`/settings/table-type-pricings/${pricingId}/update/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка сервера');
        }

        showNotification('Цены успешно обновлены!', 'success');
        closeModal('addTableTypePricingModal');

        // Обновить страницу через 1 секунду
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Ошибка обновления цен:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        saveButton.innerHTML = 'Сохранить';
        saveButton.disabled = false;
    }
}

// Универсальные функции для работы с модальными окнами
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(`${modalId}Backdrop`);
    const content = document.getElementById(`${modalId}Content`);

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    setTimeout(() => {
        backdrop.classList.add('opacity-100');
        content.classList.add('opacity-100', 'translate-y-0');
    }, 10);
}



// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок редактирования
    document.querySelectorAll('[onclick^="openEditTableTypePricingModal"]').forEach(btn => {
        const match = btn.getAttribute('onclick').match(/openEditTableTypePricingModal\((\d+)\)/);
        if (match) {
            btn.addEventListener('click', () => openEditTableTypePricingModal(match[1]));
        }
    });
});

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    // Реализация показа уведомлений
    alert(`${type.toUpperCase()}: ${message}`);
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
// async function openEditMembershipModal(membershipId) {
//   try {
//     // Получаем элементы модального окна
//     const modal = document.getElementById('membership-modal');
//     const modalContent = modal.querySelector('.modal-content');
//     const modalTitle = document.getElementById('modal-title');
//     const form = document.getElementById('membershipForm');
//
//     // Сохраняем исходное содержимое модального окна
//     const originalContent = modalContent.innerHTML;
//
//     // Показываем индикатор загрузки
//     modalContent.innerHTML = `
//       <div class="flex justify-center items-center h-64">
//         <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
//       </div>
//     `;
//
//     // Открываем модальное окно
//     modal.classList.remove('hidden');
//     document.body.classList.add('overflow-hidden');
//
//     // Загружаем данные абонемента с сервера
//     const response = await fetch(`/settings/membership/${membershipId}/view/`);
//
//     if (!response.ok) {
//       throw new Error('Не удалось загрузить данные абонемента');
//     }
//
//     const membershipData = await response.json();
//
//     // Восстанавливаем содержимое модального окна
//     modalContent.innerHTML = originalContent;
//
//     // Обновляем заголовок
//     modalTitle.textContent = 'Редактировать абонемент';
//
//     // Заполняем форму данными
//     form.reset();
//     form.action = `/settings/membership/${membershipId}/update/`;
//
//     // Основные поля
//     form.querySelector('[name="name"]').value = membershipData.name || '';
//     form.querySelector('[name="description"]').value = membershipData.description || '';
//     form.querySelector('[name="duration_days"]').value = membershipData.duration_days || '';
//     form.querySelector('[name="price"]').value = membershipData.price || '';
//
//     // Чекбоксы
//     form.querySelector('[name="is_active"]').checked = membershipData.is_active || false;
//     form.querySelector('[name="includes_booking"]').checked = membershipData.includes_booking || false;
//     form.querySelector('[name="includes_discount"]').checked = membershipData.includes_discount || false;
//     form.querySelector('[name="includes_tournaments"]').checked = membershipData.includes_tournaments || false;
//     form.querySelector('[name="includes_training"]').checked = membershipData.includes_training || false;
//
//     // Добавляем скрытое поле для метода PUT/PATCH если нужно
//     if (!form.querySelector('[name="_method"]')) {
//       const methodInput = document.createElement('input');
//       methodInput.type = 'hidden';
//       methodInput.name = '_method';
//       methodInput.value = 'PUT';
//       form.appendChild(methodInput);
//     }
//
//   } catch (error) {
//     console.error('Ошибка загрузки абонемента:', error);
//
//     // Восстанавливаем модальное окно в исходное состояние
//     modalContent.innerHTML = originalContent;
//     modalTitle.textContent = 'Добавить новый абонемент';
//     document.getElementById('membershipForm').action = '{% url "admin_settings:membership_type_create" %}';
//
//     // Показываем сообщение об ошибке
//     showNotification(`Ошибка: ${error.message}`, 'error');
//
//     // Закрываем модальное окно
//     closeMembershipModal();
//   }
// }

// Функция для показа уведомлений

// Функция для закрытия модального окна
function closeMembershipModal() {
    const modal = document.getElementById('membership-modal');
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

/**
 * Обновление абонемента
 */




async function deleteMembership(membershipId) {
    if (!confirm('Вы уверены, что хотите удалить это предложение?')) return;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch(`/settings/membership/${membershipId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            }
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Ошибка сервера');
        }

        showNotification('Абонемент успешно удалено!', 'success');

        // Обновляем страницу через 0.5 секунды
        setTimeout(() => {
            window.location.reload();
        }, 500);

    } catch (error) {
        console.error('Error deleting special offer:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}


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
            const response = await fetch(`/settings/membership/${membershipId}/update/`, {
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
            closeModal('membership-modal');

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


// ==============================================
// Универсальные функции для работы с модальными окнами
// ==============================================

/**
 * Универсальная функция открытия модального окна
 */

// Инициализация всех обработчиков при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Обработчики для Special Offer Modal
    document.getElementById('closeSpecialOfferModal')?.addEventListener('click', closeSpecialOfferModal);
    document.getElementById('cancelSpecialOffer')?.addEventListener('click', closeSpecialOfferModal);
    document.getElementById('specialOfferBackdrop')?.addEventListener('click', closeSpecialOfferModal);

    // Можно добавить аналогичные обработчики для других модальных окон
    // или использовать универсальный подход из initModals()
});

// Вспомогательная функция для показа уведомлений
