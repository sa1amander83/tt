/**==============================================
 //          Функции для работы с Special Offers
 // ==============================================
 ..
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
           fillSpecialOfferForm(form, offerData.data)
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
    console.log('Fetching offer data for ID:', offerId); // Логируем ID
    const response = await fetch(`/management/special-offers/${offerId}/`);
    console.log('Response status:', response.status); // Логируем статус ответа

    if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText); // Логируем текст ошибки
        throw new Error('Не удалось загрузить данные предложения');
    }

    const data = await response.json();
    console.log('Received data:', data); // Логируем полученные данные
    return data;
}

/**
 * Заполнение формы данными предложения
 */
/**
 * Заполняет форму редактирования спецпредложения данными
 * @param {HTMLFormElement} form - DOM-элемент формы
 * @param {Object} data - Данные предложения с сервера
 */
function fillSpecialOfferForm(form, data) {
    console.log('Filling form with data:', data);

    if (!form || !data || !data.id) {
        console.error('Invalid form or data');
        return;
    }

    // Основные поля
    form.querySelector('[name="name"]').value = data.name || '';
    form.querySelector('[name="description"]').value = data.description || '';
    form.querySelector('[name="discount_percent"]').value = data.discount_percent || '';

    // Даты
    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        try {
            return new Date(dateStr).toISOString().split('T')[0];
        } catch (e) {
            console.error('Invalid date format:', dateStr);
            return '';
        }
    };

    form.querySelector('[name="valid_from"]').value = formatDate(data.valid_from);
    form.querySelector('[name="valid_to"]').value = formatDate(data.valid_to);

    // Время
    form.querySelector('[name="time_from"]').value = data.time_from || '';
    form.querySelector('[name="time_to"]').value = data.time_to || '';

    // Чекбоксы
    form.querySelector('[name="is_active"]').checked = Boolean(data.is_active);
    const applyToAllChecked = Boolean(data.apply_to_all);
    form.querySelector('[name="apply_to_all"]').checked = applyToAllChecked;

    // Таблицы
    const tableSelect = form.querySelector('#id_tables');
    if (tableSelect && data.tables) {
        Array.from(tableSelect.options).forEach(opt => opt.selected = false);

        if (!applyToAllChecked && data.tables.length > 0) {
            data.tables.forEach(table => {
                const option = Array.from(tableSelect.options)
                    .find(opt => parseInt(opt.value) === table.id);
                if (option) option.selected = true;
            });
        }
    }

    // Дни недели
    if (data.weekdays) {
        const daysArray = typeof data.weekdays === 'string'
            ? data.weekdays.split(',')
            : Array.isArray(data.weekdays)
                ? data.weekdays.map(String)
                : [];

        form.querySelectorAll('input[name="weekdays"]').forEach(checkbox => {
            checkbox.checked = daysArray.includes(checkbox.value);
        });
    }

    // Блокировка выбора столов
    const tableSelection = document.getElementById('tableSelection');
    if (tableSelection) {
        tableSelection.classList.toggle('opacity-50', applyToAllChecked);
        tableSelection.classList.toggle('pointer-events-none', applyToAllChecked);
    }

    // ID предложения
    form.dataset.offerId = data.id;
    console.log('Form filled successfully');
}/**
 * Сохранение специального предложения
 */
async function saveSpecialOffer() {
    const form = document.getElementById('SpecialOfferForm');
    const saveBtn = document.getElementById('SaveSpecialOffer');
    const offerId = form.dataset.offerId;
    const isEditMode = !!offerId;
    const applyToAll = form.querySelector('[name="apply_to_all"]').checked;
    const selectedTables = Array.from(form.querySelector('#id_tables').selectedOptions).length;
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    if (!applyToAll && selectedTables === 0) {
        showNotification('Выберите столы или отметьте "Применять ко всем столам"', 'error');
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
        // const selectedTables = Array.from(form.querySelector('#id_tables').selectedOptions)
        //     .map(opt => opt.value);
        // formData.delete('tables'); // Удаляем старые значения
        // selectedTables.forEach(tableId => formData.append('tables', tableId));

        // Для дней недели (weekdays)
        const selectedDays = Array.from(form.querySelectorAll('[name="weekdays"]:checked'))
            .map(checkbox => checkbox.value);
        formData.delete('weekdays'); // Удаляем старые значения
        selectedDays.forEach(day => formData.append('weekdays', day));

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Определяем URL и метод
        const url = isEditMode
            ? `/management/special-offers/${offerId}/update/`
            : '/management/special-offers/create/';

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

        const response = await fetch(`/management/special-offers/${offerId}/delete/`, {
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
        applyToAllCheckbox.addEventListener('change', function () {
            tableSelection.classList.toggle('opacity-50', this.checked);
            tableSelection.classList.toggle('pointer-events-none', this.checked);
        });
    }

    // Обработчики для кнопок редактирования в таблице
    document.querySelectorAll('[onclick^="SpecialOfferModal"]').forEach(btn => {
        const match = btn.getAttribute('onclick').match(/SpecialOfferModal\((\d+)\)/);
        if (match) {
            btn.addEventListener('click', () => openSpecialOfferModal(match[1]));
        }
    });

    // Обработчики для кнопок удаления в таблице


});