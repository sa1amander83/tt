/**==============================================
 //          Table Type Pricing Functions
 // ============================================== */

// Modal control functions
function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

// Вместо этого:
document.querySelectorAll('[data-edit-pricing]').forEach(btn => {
    btn.addEventListener('click', () => {
        const pricingId = btn.dataset.editPricing;
        openTableTypePricingModal(pricingId);
    });
});

// Добавьте обработчик для кнопок удаления:
document.querySelectorAll('[data-delete-pricing]').forEach(btn => {
    btn.addEventListener('click', () => {
        const pricingId = btn.dataset.deletePricing;
        deleteTableTypePricing(pricingId);
    });
});

/**
 * Open modal for creating/editing pricing
 */
async function openTableTypePricingModal(pricingId = null) {
    try {
        const modal = document.getElementById('addTableTypePricingModal');
        const modalTitle = document.getElementById('modalTitle');
        const pricingIdInput = document.getElementById('pricingIdInput');
        const modalBody = document.getElementById('modalBody');
        const form = document.getElementById('tableTypePricingForm');

        if (!modal || !modalTitle || !pricingIdInput || !modalBody) {
            throw new Error('Required DOM elements not found');
        }

        // Если форма уже существует, просто сбросим ее
        if (form) {
            form.reset();
        } else {
            // Если формы нет, загрузим шаблон
            modalBody.innerHTML = `
                <form id="tableTypePricingForm" class="space-y-3">
                    {% csrf_token %}
                    <input type="hidden" name="pricing_id" id="pricingIdInput" value="">
                    
                    <div class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Тип стола*</label>
                            <select name="table_type" id="tableTypeSelect" required class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                                <option value="">Выберите тип</option>
                                {% for table_type in table_types %}
                                <option value="{{ table_type.id }}">{{ table_type.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Тарифный план*</label>
                            <select name="pricing_plan" id="pricingPlanSelect" required class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                                <option value="">Выберите тариф</option>
                                {% for plan in pricing_plans %}
                                <option value="{{ plan.id }}">{{ plan.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- Остальные поля формы -->
                    <div class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Цена за час (₽)*</label>
                            <input type="number" name="hour_rate" id="hourRateInput" required min="0" class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Групповая цена (₽)*</label>
                            <input type="number" name="hour_rate_group" id="hourRateGroupInput" required min="0" class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                        </div>
                    </div>

                    <div class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Цена за полчаса(₽)*</label>
                            <input type="number" name="half_hour_rate" id="halfHourRateInput" required min="0" class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                        </div>
                        
                    </div>



                    <div class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Мин. время игры (мин)*</label>
                            <input type="number" name="min_duration" id="minDurationInput" required min="0" class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Макс. время игры (мин)*</label>
                            <input type="number" name="max_duration" id="maxDurationInput" required min="0"  step="30" class="w-full px-3 py-1.5 text-sm border-2 border-gray-300 rounded-lg">
                        </div>
                    </div>
                </form>
            `;
        }

        modalTitle.textContent = pricingId ? 'Редактировать цену' : 'Новая цена для типа стола';
        document.getElementById('pricingIdInput').value = pricingId || '';

        openModal('addTableTypePricingModal');

        if (pricingId) {
            const pricingData = await fetchTableTypePricingData(pricingId);
            if (!pricingData) {
                throw new Error('No pricing data received');
            }
            fillPricingForm(pricingData);
        }

    } catch (error) {
        console.error('Error opening pricing modal:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
        closeModal('addTableTypePricingModal');
    }
}


async function fetchTableTypePricingData(pricingId) {
    const response = await fetch(`/settings/table-type-pricings/${pricingId}/`);
    if (!response.ok) {
        throw new Error('Failed to load pricing data');
    }
    const data = await response.json();

    // Проверка структуры данных
    if (!data || typeof data !== 'object') {
        throw new Error('Invalid data format received');
    }

    return data;
}

/**
 * Fill form with pricing data
 */
function fillPricingForm(data) {
    const fields = {
        'tableTypeSelect': data.table_type?.id || '',
        'pricingPlanSelect': data.pricing_plan?.id || '',
        'hourRateInput': data.hour_rate || '',
        'halfHourRateInput': data.half_hour_rate || '',
        'hourRateGroupInput': data.hour_rate_group || '',
        'minDurationInput': data.min_duration || '',
        'maxDurationInput': data.max_duration || ''
    };

    for (const [id, value] of Object.entries(fields)) {
        const element = document.getElementById(id);
        if (element) {
            element.value = value;
        } else {
            console.error(`Element with ID ${id} not found`);
        }
    }
}

/**
 * Save pricing data
 */
async function saveTableTypePricing() {
    const form = document.getElementById('tableTypePricingForm');
    const saveBtn = document.getElementById('saveButton');
    const pricingIdInput = document.getElementById('pricingIdInput');

    if (!form || !saveBtn || !pricingIdInput) {
        showNotification('Системная ошибка: элементы формы не найдены', 'error');
        return;
    }

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        // Show loading state
        saveBtn.innerHTML = `
            <span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full"></span>
            Сохранение...
        `;
        saveBtn.disabled = true;

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const pricingId = pricingIdInput.value.trim();

        // Определяем URL и метод в зависимости от наличия ID
        const url = pricingId
            ? `/settings/table-type-pricings/${pricingId}/update/`
            : '/settings/table-type-pricings/create/';

        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка сервера');
        }

        const result = await response.json();

        showNotification(
            pricingId ? 'Цена успешно обновлена!' : 'Новая цена создана!',
            'success'
        );

        closeModal('addTableTypePricingModal');
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        console.error('Save pricing error:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        if (saveBtn) {
            saveBtn.innerHTML = 'Сохранить';
            saveBtn.disabled = false;
        }
    }
}

/**
 * Delete pricing
 */
async function deleteTableTypePricing(pricingId) {
    if (!confirm('Вы уверены, что хотите удалить эту цену?')) return;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch(`/settings/table-type-pricings/${pricingId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete pricing');
        }

        showNotification('Цена успешно удалена!', 'success');
        setTimeout(() => window.location.reload(), 500);

    } catch (error) {
        console.error('Delete pricing error:', error);
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

// Initialize event listeners

    // Edit buttons in table
    document.querySelectorAll('[data-edit-pricing]').forEach(btn => {
        btn.addEventListener('click', () => {
            const pricingId = btn.dataset.editPricing;
            openTableTypePricingModal(pricingId);
        });
    });


document.addEventListener('click', (e) => {
  if (e.target && e.target.id === 'saveButton') {
    saveTableTypePricing();
  }
});