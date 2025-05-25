document.addEventListener('DOMContentLoaded', function () {
    // Инициализация с проверкой активной кнопки
    let selectedViewMode = (() => {
        const activeBtn = document.querySelector('.slot-view-btn.bg-white');
        return activeBtn ? parseInt(activeBtn.dataset.value) :
            parseInt('{{ user.slot_view_mode|default:60 }}') || 60;
    })();

    // Обработчик выбора режима
    document.querySelectorAll('.slot-view-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.slot-view-btn').forEach(b => {
                b.classList.remove('bg-white', 'shadow-md', 'text-green-600');
                b.classList.add('text-gray-500', 'hover:text-gray-700');
            });

            this.classList.add('bg-white', 'shadow-md', 'text-green-600');
            this.classList.remove('text-gray-500', 'hover:text-gray-700');

            selectedViewMode = parseInt(this.dataset.value);
            console.log('Выбрано:', selectedViewMode); // Для отладки
        });
    });

    // Обработчик сохранения с двойной проверкой
    document.getElementById('save-slot-view-mode-btn').addEventListener('click', function () {
        // Дополнительная проверка активной кнопки
        const activeBtn = document.querySelector('.slot-view-btn.bg-white');
        if (activeBtn) {
            selectedViewMode = parseInt(activeBtn.dataset.value);
        }

        console.log('Отправляем:', selectedViewMode); // Для отладки

        const btn = this;
        const originalText = btn.textContent;

        btn.disabled = true;
       

        fetch('/accounts/update-slot-view-mode/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                slot_view_mode: selectedViewMode
            })
        })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сохранения');
                return response.json();
            })
            .then(data => {
                showNotification('Настройки сохранены!', 'success');
                if (data.refresh_required) setTimeout(() => location.reload(), 1000);
            })
            .catch(error => {
                console.error('Ошибка:', error);
                showNotification('Ошибка сохранения', 'error');
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = originalText;
            });
    });


// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-md shadow-lg text-white font-medium z-50 animate-fade-in 
                            ${type === 'success' ? 'bg-green-500' : 'bg-red-500'}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.remove('animate-fade-in');
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Вспомогательная функция для получения CSRF токена
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
})
;