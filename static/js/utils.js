window.getCSRFToken = function () {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue;
}

window.formatDate = function(dateStr, options = {}) {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;

    return d.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      ...options
    });
  } catch (e) {
    console.error('Date formatting error:', e);
    return dateStr;
  }
}

window.debounce=function(fn, delay = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

window.safeParseJSON=function(response) {
  return response.text().then(text => {
    try {
      return text ? JSON.parse(text) : null;
    } catch (e) {
      console.error('JSON parse error:', e);
      throw new Error('Invalid JSON response');
    }
  });
}


window.showNotification=function (message, type) {
    const types = {
        'info': 'bg-blue-100 text-blue-800',
        'success': 'bg-green-100 text-green-800',
        'warning': 'bg-yellow-100 text-yellow-800',
        'error': 'bg-red-100 text-red-800'
    };

    const container = document.getElementById('notification');
    if (!container) {
        console.error('Notification container with id="notification" not found');
        return;
    }

    const notification = document.createElement('div');
    notification.className = `px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center transform transition-all duration-300 ${
        types[type]
    } opacity-0 translate-x-full`;

    notification.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${
        type === 'success' ? 'M5 13l4 4L19 7' : 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    }"></path>
        </svg>
        ${message}
    `;

    container.appendChild(notification);

    // Показываем уведомление с анимацией
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
    }, 10); // небольшая задержка для инициализации

    // Скрываем и удаляем уведомление через 5 секунд
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300); // время на завершение анимации
    }, 5000); // общее время показа уведомления
}