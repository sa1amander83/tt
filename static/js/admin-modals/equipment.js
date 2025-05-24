document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const addPriceModal = document.querySelector('[data-modal="equipment-pricing"]');

    // Form elements
    const addForm = document.getElementById('add-equipment-form');
    const editForm = document.getElementById('edit-equipment-form');

    // Buttons
    const editButtons = document.querySelectorAll('[data-edit-equip]');
    const deleteButtons = document.querySelectorAll('[data-delete-equip]');

    // Initialize modals
    if (addPriceModal) {
        addPriceModal.addEventListener('click', function(e) {
            e.preventDefault();
            showAddModal();
        });
    }

    // Edit button handlers - переработанный обработчик
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const equipId = this.getAttribute('data-edit-equip');
            loadEquipmentData(equipId);
        });
    });

    // Delete button handlers
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const equipId = this.getAttribute('data-delete-equip');
            if (confirm('Вы уверены, что хотите удалить это оборудование?')) {
                deleteEquipment(equipId);
            }
        });
    });

    // Add form submission
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createEquipment();
        });
    }

    // Edit form submission
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const equipId = document.getElementById('edit-equip-id').value;
            updateEquipment(equipId);
        });
    }

    // Function to show add modal
    function showAddModal() {
        const modal = document.getElementById('add-equipment-modal');
        const backdrop = modal.querySelector('.bg-black\\/50');
        const content = modal.querySelector('.relative');

        if (addForm) addForm.reset();

        modal.classList.remove('hidden');
        setTimeout(() => {
            backdrop.style.opacity = '1';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0)';
        }, 10);
    }

    // Function to show edit modal
    function showEditModal() {
        const modal = document.getElementById('edit-equipment-modal');
        const backdrop = modal.querySelector('.bg-black\\/50');
        const content = modal.querySelector('.relative');

        modal.classList.remove('hidden');
        setTimeout(() => {
            backdrop.style.opacity = '1';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0)';
        }, 10);
    }

    // Function to load equipment data for editing - переработанная функция
    function loadEquipmentData(equipId) {
        fetch(`/settings/api/equipment/${equipId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Устанавливаем ID оборудования в скрытое поле
                document.getElementById('edit-equip-id').value = equipId;

                // Заполняем форму данными
                document.getElementById('edit-name').value = data.name;
                document.getElementById('edit-description').value = data.description || '';
                document.getElementById('edit-price-hour').value = data.price_per_hour;
                document.getElementById('edit-price-half-hour').value = data.price_per_half_hour;
                document.getElementById('edit-available').checked = data.is_available;

                // Показываем модальное окно
                showEditModal();
            } else {
                alert('Ошибка при загрузке данных: ' + (data.message || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при загрузке данных оборудования: ' + error.message);
        });
    }
    // Function to create new equipment
    function createEquipment() {
        const formData = {
            name: document.getElementById('add-name').value,
            description: document.getElementById('add-description').value,
            price_per_hour: document.getElementById('add-price-hour').value,
            price_per_half_hour: document.getElementById('add-price-half-hour').value,
            is_available: document.getElementById('add-available').checked
        };

        fetch('/settings/api/equipment/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Close modal and refresh the page
                // Example: MicroModal.close('add-equipment-modal');
                location.reload();
            } else {
                alert('Ошибка при создании: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при создании оборудования');
        });
    }

    // Function to update equipment
    function updateEquipment(equipId) {
        const formData = {
            name: document.getElementById('edit-name').value,
            description: document.getElementById('edit-description').value,
            price_per_hour: document.getElementById('edit-price-hour').value,
            price_per_half_hour: document.getElementById('edit-price-half-hour').value,
            is_available: document.getElementById('edit-available').checked
        };

        fetch(`/settings/api/equipment/${equipId}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Close modal and refresh the page
                // Example: MicroModal.close('edit-equipment-modal');
                location.reload();
            } else {
                alert('Ошибка при обновлении: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при обновлении оборудования');
        });
    }

    // Function to delete equipment
    function deleteEquipment(equipId) {
        fetch(`/settings/api/equipment/${equipId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка при удалении: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при удалении оборудования');
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});