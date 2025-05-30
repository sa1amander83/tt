// Promo Code Modal Functions
function openPromoCodeModal(promoId = null) {
    const modal = document.getElementById('promocode-modal');
    const title = document.getElementById('promo-modal-title');
    const form = document.getElementById('promoCodeForm');

    if (promoId) {
        // Edit mode - load promo code data
        title.textContent = 'Редактировать промокод';
        document.getElementById('promo_id').value = promoId;

        // Here you would fetch the promo code data and fill the form
        // Example (you'll need to implement the API endpoint):
        fetch(`/api/promocodes/${promoId}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('id_promo_code').value = data.code;
                document.getElementById('id_promo_description').value = data.description;
                document.getElementById('id_discount_percent').value = data.discount_percent;
                document.getElementById('id_usage_limit').value = data.usage_limit || '';
                document.getElementById('id_valid_from').value = data.valid_from;
                document.getElementById('id_valid_to').value = data.valid_to;
                document.getElementById('id_promo_user').value = data.user || '';
                document.getElementById('id_promo_active').checked = data.is_active;
            });
    } else {
        // Create mode - reset form
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

function savePromoCode() {
    const form = document.getElementById('promoCodeForm');
    const formData = new FormData(form);
    const promoId = formData.get('promo_id');
    const isEdit = !!promoId;

    // Convert to JSON
    const data = {};
    formData.forEach((value, key) => {
        if (value !== '') data[key] = value;
    });

    // Here you would send the data to your API
    const url = isEdit ? `/api/promocodes/${promoId}/` : '/api/promocodes/';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closePromoCodeModal();
            // Reload the page or update the table dynamically
            window.location.reload();
        } else {
            alert(data.error || 'Ошибка при сохранении промокода');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при сохранении');
    });
}

function deletePromoCode(promoId) {
    if (confirm('Вы уверены, что хотите удалить этот промокод?')) {
        fetch(`/api/promocodes/${promoId}/`, {
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