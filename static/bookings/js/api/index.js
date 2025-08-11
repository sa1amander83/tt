const BASE = '';

const csrfToken = window.getCSRFToken || '';

const headers = () => ({
  'Content-Type': 'application/json',
  'X-CSRFToken' : csrfToken
});

const request = (url, opts = {}) =>
  fetch(BASE + url, { credentials: 'include', ...opts })
    .then(r => {
      if (!r.ok) throw new Error(r.statusText);
      return r.json();
    });

export const get  = (url) => request(url, { method: 'GET' });
export const post = (url, body) =>
  request(url, { method: 'POST', headers: headers(), body: JSON.stringify(body) });