function csrf() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.match(/csrftoken=([^;]+)/)?.[1];
}

export const BookingAPI = {

  async create(payload) {
    return fetch('/bookings/api/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
      body: JSON.stringify(payload),
      credentials: 'include'
    }).then(r => r.ok ? r.json() : r.json().then(err => Promise.reject(err)));

  },

  async cancel(id) {
    return fetch(`/bookings/api/cancel/${id}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf() },
      credentials: 'include'
    });
  },

  async payment(id) {
    return fetch('/bookings/api/payment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
      body: JSON.stringify({ booking_id: id }),
      credentials: 'include'
    }).then(r => r.ok ? r.json() : r.json().then(err => Promise.reject(err)));
  },
    async get(id) {
    return fetch(`/bookings/api/${id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf()
      },
      credentials: 'include'
    }).then(r => {
      if (!r.ok) {
        return r.json().then(err => Promise.reject(err));
      }
      return r.json();
    });
  },

};