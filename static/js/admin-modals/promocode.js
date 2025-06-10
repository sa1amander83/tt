// Открыть модалку
async function openPromoCodeModal(promoId = null) {
    const modal = document.getElementById('promocode-modal');
    const title = document.getElementById('promo-modal-title');
    const form = document.getElementById('promoCodeForm');

    if (promoId) {
        title.textContent = 'Редактировать промокод';
        document.getElementById('promo_id').value = promoId;

        try {
            const response = await fetch(`/management/api/promocodes/${promoId}/`);
            if (!response.ok) throw new Error(`Ошибка ${response.status}`);

            const data = await response.json();

            // Заполнение полей формы
            document.getElementById('id_promo_code').value = data.code;
            document.getElementById('id_promo_description').value = data.description || '';
            document.getElementById('id_discount_percent').value = data.discount_percent;
            document.getElementById('id_usage_limit').value = data.usage_limit ?? '';
            document.getElementById('id_valid_from').value = data.valid_from;
            document.getElementById('id_valid_to').value = data.valid_to;
            document.getElementById('id_promo_user').value = data.user ?? '';
            document.getElementById('id_promo_active').checked = data.is_active;
        } catch (err) {
            console.error('Ошибка загрузки промокода:', err);
            alert('Не удалось загрузить данные промокода');
            closePromoCodeModal();
            return;
        }
    } else {
        title.textContent = 'Добавить промокод';
        form.reset();
        document.getElementById('promo_id').value = '';
        document.getElementById('id_promo_active').checked = true;
    }

    modal.classList.remove('hidden');
}

// Закрыть модалку
function closePromoCodeModal() {
    document.getElementById('promocode-modal').classList.add('hidden');
}

// Сохранить промокод
async function savePromoCode() {
    const form = document.getElementById('promoCodeForm');
    const formData = new FormData(form);
    const promoId = formData.get('promo_id');
    const isEdit = !!promoId;

    const data = {
        code: formData.get('code'),
        description: formData.get('description'),
        discount_percent: parseInt(formData.get('discount_percent'), 10),
        valid_from: formData.get('valid_from'),
        valid_to: formData.get('valid_to'),
        is_active: document.getElementById('id_promo_active').checked,
        usage_limit: formData.get('usage_limit') || null,
        user: formData.get('user') || null
    };

    if (data.usage_limit !== null) {
        data.usage_limit = parseInt(data.usage_limit, 10);
        if (isNaN(data.usage_limit)) data.usage_limit = null;
    }

    // Валидация
    if (!data.code) return alert('Введите код');
    if (isNaN(data.discount_percent) || data.discount_percent < 1 || data.discount_percent > 100)
        return alert('Скидка должна быть от 1 до 100');
    if (!data.valid_from || !data.valid_to)
        return alert('Укажите даты');
    if (data.valid_from > data.valid_to)
        return alert('Дата окончания не может быть раньше начала');

    const url = isEdit ? `/management/api/promocodes/${promoId}/` : '/management/api/promocodes/';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            const msg = errData.detail || JSON.stringify(errData);
            throw new Error(msg);
        }

        closePromoCodeModal();
        window.location.reload();
    } catch (err) {
        console.error('Ошибка сохранения:', err);
        alert(err.message || 'Не удалось сохранить промокод');
    }
}

// Удаление промокода
function deletePromoCode(promoId) {
    if (!confirm('Удалить промокод?')) return;

    fetch(`/api/promocodes/${promoId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Ошибка при удалении');
            }
        })
        .catch(error => {
            console.error('Ошибка удаления:', error);
            alert('Не удалось удалить промокод');
        });
}

// Открыть модалку редактирования
function openEditPromoCodeModal(promoId) {
    openPromoCodeModal(promoId);
}
