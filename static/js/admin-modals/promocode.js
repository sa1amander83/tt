    // Promo Code Modal Functions
    async function openPromoCodeModal(promoId = null) {
        const modal = document.getElementById('promocode-modal');
        const title = document.getElementById('promo-modal-title');
        const form = document.getElementById('promoCodeForm');

        if (promoId) {
            title.textContent = 'Редактировать промокод';
            document.getElementById('promo_id').value = promoId;

            try {
                const response = await fetch(`/management/promocodes/${promoId}/`);

                if (!response.ok) {
                    throw new Error(`Failed to load promo code: ${response.status}`);
                }

                const data = await response.json();

                // Fill form fields
                document.getElementById('id_promo_code').value = data.code;
                document.getElementById('id_promo_description').value = data.description || '';
                document.getElementById('id_discount_percent').value = data.discount_percent;
                document.getElementById('id_usage_limit').value = data.usage_limit || '';
                document.getElementById('id_valid_from').value = data.valid_from;
                document.getElementById('id_valid_to').value = data.valid_to;
                document.getElementById('id_promo_user').value = data.user || '';
                document.getElementById('id_promo_active').checked = data.is_active;
            } catch (error) {
                console.error('Error loading promo code:', error);
                alert('Failed to load promo code details');
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

    function closePromoCodeModal() {
        document.getElementById('promocode-modal').classList.add('hidden');
    }

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

    // Числовая проверка
    if (data.usage_limit !== null) {
        data.usage_limit = parseInt(data.usage_limit, 10);
        if (isNaN(data.usage_limit)) data.usage_limit = null;
    }

    const url = isEdit ? `/management/promocodes/${promoId}/` : '/management/promocodes/create/';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        });

        const contentType = response.headers.get("content-type") || "";
        const isJson = contentType.includes("application/json");
        const responseData = isJson ? await response.json() : null;

        if (!response.ok) {
            const message = responseData?.error || `Ошибка ${response.status}: ${response.statusText}`;
            throw new Error(message);
        }

        closePromoCodeModal();
        window.location.reload();
    } catch (error) {
        console.error('Ошибка сохранения промокода:', error);
        alert(error.message || 'Не удалось сохранить промокод');
    }
}

    function deletePromoCode(promoId) {
        if (confirm('Вы уверены, что хотите удалить этот промокод?')) {
            fetch(`/management/promocodes/${promoId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Ошибка при удалении промокода');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при удалении');
                });
        }
    }

    function openEditPromoCodeModal(promoId) {
        openPromoCodeModal(promoId);
    }