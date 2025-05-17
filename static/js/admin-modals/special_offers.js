// ==============================================
// Функции для работы с Special Offers
// ==============================================

/**
 * Открытие модального окна для создания/редактирования Special Offer
 */
async function openSpecialOfferModal(offerId = null) {
    try {
        const modal = document.getElementById('addSpecialOfferModal');
        const form = document.getElementById('SpecialOfferForm');
        
        // Сброс формы и заголовка
        form.reset();
        modal.querySelector('h3').textContent = offerId 
            ? 'Редактировать предложение' 
            : 'Новое спецпредложение';

        // Если это редактирование - загружаем данные
        if (offerId) {
            const offerData = await fetchSpecialOfferData(offerId);
            fillSpecialOfferForm(form, offerData);
            form.dataset.offerId = offerId;
        }

        // Показываем модальное окно
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');

        // Анимация появления
        setTimeout(() => {
            const backdrop = document.getElementById('specialOfferBackdrop');
            const content = document.getElementById('specialOfferModalContent');
            backdrop.classList.add('opacity-100');
            content.classList.add('opacity-100', 'scale-100');
        }, 10);

    } catch (error) {
        console.error('Error opening special offer modal:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

/**
 * Загрузка данных специального предложения с сервера
 */
async function fetchSpecialOfferData(offerId) {
    const response = await fetch(`/settings/special-offers/${offerId}/`);
    if (!response.ok) {
        throw new Error('Не удалось загрузить данные предложения');
    }
    return await response.json();
}

/**
 * Заполнение формы данными предложения
 */
function fillSpecialOfferForm(form, data) {
    form.querySelector('[name="name"]').value = data.name || '';
    form.querySelector('[name="description"]').value = data.description || '';
    form.querySelector('[name="discount_percent"]').value = data.discount_percent || '';
    form.querySelector('[name="valid_from"]').value = data.valid_from || '';
    form.querySelector('[name="valid_to"]').value = data.valid_to || '';
    form.querySelector('[name="is_active"]').checked = data.is_active || false;
    form.querySelector('[name="apply_to_all"]').checked = data.apply_to_all || false;
    form.querySelector('[name="time_from"]').value = data.time_from || false;
    form.querySelector('[name="time_to"]').value = data.time_to || false;

    
    // Обработка выбора столов (если не "применить ко всем")
    if (!data.apply_to_all && data.tables) {
        const tableSelect = form.querySelector('[name="tables"]');
        if (tableSelect) {
            data.tables.forEach(table => {
                const option = tableSelect.querySelector(`option[value="${table.id}"]`);
                if (option) option.selected = true;
            });
        }
    }
    if (data.weekdays) {
    const weekdays = data.weekdays.split(',');
    weekdays.forEach(day => {
        const checkbox = form.querySelector(`input[name="weekdays"][value="${day.value}"]`);
        if (checkbox) checkbox.checked = true;
    });
}
}

/**
 * Сохранение специального предложения
 */
async function saveSpecialOffer() {
    const form = document.getElementById('SpecialOfferForm');
    const saveBtn = document.getElementById('SaveSpecialOffer');
    const offerId = form.dataset.offerId;
    const isEditMode = !!offerId;

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        // Показать состояние загрузки
        saveBtn.innerHTML = `
            <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full"></span>
            Сохранение...
        `;
        saveBtn.disabled = true;

        // Подготовка данных формы
        const formData = new FormData(form);

        // Для полей many-to-many нужно передавать массив значений
        const selectedTables = Array.from(form.querySelector('#id_tables').selectedOptions)
            .map(opt => opt.value);
        formData.delete('tables'); // Удаляем старые значения
        selectedTables.forEach(tableId => formData.append('tables', tableId));

        // Для дней недели (weekdays)
        const selectedDays = Array.from(form.querySelectorAll('[name="weekdays"]:checked'))
            .map(checkbox => checkbox.value);
        formData.delete('weekdays'); // Удаляем старые значения
        selectedDays.forEach(day => formData.append('weekdays', day));

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Определяем URL и метод
        const url = isEditMode
            ? `/settings/special-offers/${offerId}/update/`
            : '/settings/special-offers/create/';

        // Отправляем запрос
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            }
        });

        const data = await response.json();

        if (!response.ok) {
            // Выводим ошибки валидации, если они есть
            if (data.errors) {
                let errorMessages = [];
                for (const [field, errors] of Object.entries(data.errors)) {
                    errorMessages.push(`${field}: ${errors.join(', ')}`);
                }
                throw new Error(errorMessages.join('\n'));
            }
            throw new Error(data.message || 'Ошибка сервера');
        }

        showNotification(
            isEditMode
                ? 'Предложение успешно обновлено!'
                : 'Предложение успешно создано!',
            'success'
        );

        closeSpecialOfferModal();

        // Обновляем страницу через 1 секунду
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Error saving special offer:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        saveBtn.innerHTML = 'Сохранить';
        saveBtn.disabled = false;
    }
}
/**
 * Удаление специального предложения
 */
async function deleteSpecialOffer(offerId) {
    if (!confirm('Вы уверены, что хотите удалить это предложение?')) return;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch(`/settings/special-offers/${offerId}/delete/`, {
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

        showNotification('Предложение успешно удалено!', 'success');
        
        // Обновляем страницу через 0.5 секунды
        setTimeout(() => {
            window.location.reload();
        }, 500);

    } catch (error) {
        console.error('Error deleting special offer:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

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

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', () => {
    // Обработчик для кнопки сохранения
    document.getElementById('SaveSpecialOffer')?.addEventListener('click', saveSpecialOffer);
    
    // Обработчик для чекбокса "Применить ко всем"
    const applyToAllCheckbox = document.getElementById('applyToAll');
    const tableSelection = document.getElementById('tableSelection');
    
    if (applyToAllCheckbox && tableSelection) {
        applyToAllCheckbox.addEventListener('change', function() {
            tableSelection.classList.toggle('opacity-50', this.checked);
            tableSelection.classList.toggle('pointer-events-none', this.checked);
        });
    }
    
    // Обработчики для кнопок редактирования в таблице
    document.querySelectorAll('[onclick^="openEditSpecialOfferModal"]').forEach(btn => {
        const match = btn.getAttribute('onclick').match(/openEditSpecialOfferModal\((\d+)\)/);
        if (match) {
            btn.addEventListener('click', () => openSpecialOfferModal(match[1]));
        }
    });
    
    // Обработчики для кнопок удаления в таблице


});