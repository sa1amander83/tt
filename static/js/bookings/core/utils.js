export function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue;
}

export function formatDate(dateStr, options = {}) {
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

export function debounce(fn, delay = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

export function safeParseJSON(response) {
  return response.text().then(text => {
    try {
      return text ? JSON.parse(text) : null;
    } catch (e) {
      console.error('JSON parse error:', e);
      throw new Error('Invalid JSON response');
    }
  });
}