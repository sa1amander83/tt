  function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }

    // Создание строки таблицы для праздника
    function createHolidayRow(holidayData) {
        const row = document.createElement('tr');
        row.setAttribute('data-holiday-id', holidayData.id);
        row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            ${holidayData.date}
        </td>
        <td class="px-6 py-4 text-sm text-gray-500">
            ${holidayData.description}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm">
            <span class="px-2 py-1 text-xs font-semibold rounded-full
                ${getStatusClass(holidayData.status)}">
                ${holidayData.status}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${holidayData.open_time && holidayData.close_time
            ? `${holidayData.open_time} - ${holidayData.close_time}`
            : 'Закрыто'}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
            <a href="#" class="text-indigo-600 hover:text-indigo-900 mr-3 edit-holiday"
               data-holiday-id="${holidayData.id}">Изменить</a>
            <a href="#" class="text-red-600 hover:text-red-900 delete-holiday"
               data-holiday-id="${holidayData.id}">Удалить</a>
        </td>
    `;
        return row;
    }

    // Добавление новой строки в начало таблицы
    function updateHolidaysTable(holidayData) {
        const tbody = document.getElementById('holiday-table-body');
        const newRow = createHolidayRow(holidayData);
        tbody.insertBefore(newRow, tbody.firstChild);
    }

    // Обновление существующей строки
    function updateHolidayRow(holidayId, holidayData) {
        const row = document.querySelector(`tr[data-holiday-id="${holidayId}"]`);
        if (row) {
            row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${holidayData.date}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
                ${holidayData.description}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs font-semibold rounded-full
                    ${getStatusClass(holidayData.status)}">
                    ${holidayData.status}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${holidayData.open_time && holidayData.close_time
                ? `${holidayData.open_time} - ${holidayData.close_time}`
                : 'Закрыто'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="#" class="text-indigo-600 hover:text-indigo-900 mr-3 edit-holiday"
                   data-holiday-id="${holidayData.id}">Изменить</a>
                <a href="#" class="text-red-600 hover:text-red-900 delete-holiday"
                   data-holiday-id="${holidayData.id}">Удалить</a>
            </td>
        `;
        }
    }

    // Удаление строки
    function removeHolidayRow(holidayId) {
        const row = document.querySelector(`tr[data-holiday-id="${holidayId}"]`);
        if (row) {
            row.remove();
        }
    }

    // Классы для статусов
    function getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'closed':
                return 'bg-red-100 text-red-800';
            case 'shortened':
                return 'bg-yellow-100 text-yellow-800';
            default:
                return 'bg-green-100 text-green-800';
        }
    }

    // Уведомления
    //{#function showSuccessAlert(message) {#}
   // {#    alert(message); // Замените на кастомный алерт при желании#}
   //}

    function showErrorAlert(message, errors = null) {
        let errorMessage = message;
        if (errors) {
            errorMessage += '\n' + Object.values(errors).join('\n');
        }
        alert(errorMessage); // Замените на кастомный алерт при желании
    }

    // Создание праздничного дня
    async function createHoliday(formData) {
        try {
            const response = await fetch('/settings/holidays/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                updateHolidaysTable(data.data);
                showNotification("Праздничный день добавлен!",data.message);
                return true;
            } else {
                showErrorAlert(data.message, data.errors);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Ошибка сети');
            return false;
        }
    }

    // Редактирование праздничного дня
    async function updateHoliday(holidayId, formData) {
        try {
            const response = await fetch(`/settings/holidays/${holidayId}/update/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                updateHolidayRow(holidayId, data.data);
                showNotification("Праздничный день изменён!",data.message);
                return true;
            } else {
                showErrorAlert(data.message, data.errors);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Ошибка сети');
            return false;
        }
    }

    // Удаление праздничного дня
    async function deleteHoliday(holidayId) {
        if (!confirm('Вы уверены, что хотите удалить этот праздничный день?')) {
            return false;
        }

        try {
            const response = await fetch(`/settings/holidays/${holidayId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                removeHolidayRow(holidayId);
                showNotification("Праздничный день удалён!",data.message);
                return true;
            } else {
                showNotification("Праздничный день не удалён!",data.message);
                return false;
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Ошибка сети');
            return false;
        }
    }

    // Делегирование событий для кнопок "Изменить" и "Удалить"
    document.addEventListener('DOMContentLoaded', function () {
        const tbody = document.getElementById('holiday-table-body');
        if (tbody) {
            tbody.addEventListener('click', async function (e) {
                const editBtn = e.target.closest('.edit-holiday');
                const deleteBtn = e.target.closest('.delete-holiday');
                if (editBtn) {
                    e.preventDefault();
                    const holidayId = editBtn.dataset.holidayId;
                    await showEditHolidayModal(holidayId);
                }
                if (deleteBtn) {
                    e.preventDefault();
                    const holidayId = deleteBtn.dataset.holidayId;
                    await deleteHoliday(holidayId);
                }
            });
        }
    });

    // Модальное окно редактирования (пример, доработайте под ваш UI)
    async function showEditHolidayModal(holidayId) {
        try {
            const response = await fetch(`/settings/holidays/${holidayId}/`);
            const data = await response.json();

            if (!data || !data.id) {
                showErrorAlert('Данные не найдены.');
                return;
            }

            // Удалить существующее модальное окно, если оно уже есть
            const existingModal = document.getElementById('editHolidayModal');
            if (existingModal) existingModal.remove();

            const modal = document.createElement('div');
            modal.id = 'editHolidayModal';
            modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';

            modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg relative">
                <h2 class="text-xl font-semibold mb-4">Редактировать праздничный день</h2>
                <form id="editHolidayForm" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium mb-1">Дата</label>
                        <input type="text" name="date" class="datepicker w-full border rounded px-3 py-2" value="${data.date}" />
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Статус</label>
                        <select name="status" class="w-full border rounded px-3 py-2">
                            <option value="closed" ${data.status === 'closed' ? 'selected' : ''}>Закрыто</option>
                            <option value="shortened" ${data.status === 'shortened' ? 'selected' : ''}>Сокращённый</option>
                            <option value="open" ${data.status === 'open' ? 'selected' : ''}>Открыто</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Описание</label>
                        <input type="text" name="description" class="w-full border rounded px-3 py-2" value="${data.description || ''}" />
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium mb-1">Время открытия</label>
                            <input type="text" name="open_time" class="timepicker w-full border rounded px-3 py-2" value="${data.open_time || ''}" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">Время закрытия</label>
                            <input type="text" name="close_time" class="timepicker w-full border rounded px-3 py-2" value="${data.close_time || ''}" />
                        </div>
                    </div>
                    <div class="flex justify-end space-x-2 mt-4">
                        <button type="button" id="cancelEdit" class="px-4 py-2 bg-gray-300 rounded">Отмена</button>
                        <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded">Сохранить</button>
                    </div>
                </form>
            </div>
        `;

            document.body.appendChild(modal);

            // Инициализация flatpickr
            flatpickr('.datepicker', {dateFormat: "d.m.Y", allowInput: true, locale: "ru"});
            flatpickr('.timepicker', {enableTime: true, noCalendar: true, dateFormat: "H:i", locale: "ru"});

            // Закрытие модального окна
            modal.querySelector('#cancelEdit').addEventListener('click', () => {
                modal.remove();
            });

            // Обработка отправки формы
            document.getElementById('editHolidayForm').addEventListener('submit', async function (e) {
                e.preventDefault();

                const formData = {
                    date: this.date.value,
                    status: this.status.value,
                    description: this.description.value,
                    open_time: this.open_time.value,
                    close_time: this.close_time.value
                };

                const success = await updateHoliday(holidayId, formData);
                if (success) {
                    modal.remove();
                    showNotification("Праздничный день успешно обновлен", "success");
                }
            });

        } catch (error) {
            console.error('Error:', error);
            showNotification('Ошибка при загрузке данных', 'error');
        }
    }


