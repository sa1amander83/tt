let currentMembershipId = null;

// Открыть модалку для создания
function openMembershipModal() {
    currentMembershipId = null;
    const modal = document.getElementById('membership-modal');
    const form = document.getElementById('membershipForm');

    form.reset();
    form.action = '/settings/membership/create/';
    document.getElementById('modal-title').textContent = 'Добавить новый абонемент';
    document.getElementById('membership_id').value = '';

    clearFormErrors();
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

// Открыть модалку для редактирования
async function openEditMembershipModal(membershipId) {
    try {
        currentMembershipId = membershipId;
        const modal = document.getElementById('membership-modal');
        const form = document.getElementById('membershipForm');

        form.reset();
        clearFormErrors();

        document.getElementById('modal-title').textContent = 'Загрузка...';
        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');

        const res = await fetch(`/settings/membership/${membershipId}/view/`);
        const data = await res.json();

        document.getElementById('id_name').value = data.name || '';
        document.getElementById('id_description').value = data.description || '';
        document.getElementById('id_duration_days').value = data.duration_days || '';
        document.getElementById('id_price').value = data.price || '';

        document.getElementById('id_is_active').checked = data.is_active;
        document.getElementById('id_includes_booking').checked = data.includes_booking;
        document.getElementById('id_includes_discount').checked = data.includes_discount;
        document.getElementById('id_includes_tournaments').checked = data.includes_tournaments;
        document.getElementById('id_includes_training').checked = data.includes_training;

        // 👇 Скрытое поле с ID
        document.getElementById('membership_id').value = membershipId;

        // 👇 Обновляем экшен формы
        form.action = `/settings/membership/${membershipId}/update/`;
        document.getElementById('modal-title').textContent = 'Редактировать абонемент';
    } catch (err) {
        showNotification('Ошибка загрузки абонемента', 'error');
        closeMembershipModal();
    }
}

// Закрытие модалки
function closeMembershipModal() {
    const modal = document.getElementById('membership-modal');
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    currentMembershipId = null;
}

// Сохранение формы
 async function saveMembership() {
    const form = document.getElementById('membershipForm');
    const formData = new FormData(form);
    const saveBtn = document.getElementById('saveMembershipBtn');

    saveBtn.disabled = true;
    saveBtn.textContent = 'Сохранение...';

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'success') {
            if (data.errors) showFormErrors(data.errors);
            throw new Error(data.message || 'Ошибка при сохранении');
        }

        showNotification(currentMembershipId ? 'Абонемент обновлён' : 'Абонемент создан', 'success');
        closeMembershipModal();

        if (typeof window.updateMembershipsTable === 'function') {
            await window.updateMembershipsTable();
        } else {
            window.location.reload();
        }

    } catch (err) {
        showNotification(`Ошибка: ${err.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Сохранить';
    }
}

// Очистка ошибок
function clearFormErrors() {
    document.querySelectorAll('.form-error').forEach(e => e.remove());
    document.querySelectorAll('.border-red-500').forEach(e => e.classList.remove('border-red-500'));
}

// Показ ошибок
function showFormErrors(errors) {
    for (const field in errors) {
        const input = document.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('border-red-500');
            const errMsg = document.createElement('div');
            errMsg.className = 'form-error text-red-500 text-xs mt-1';
            errMsg.textContent = errors[field].join(', ');
            input.parentNode.appendChild(errMsg);
        }
    }
}