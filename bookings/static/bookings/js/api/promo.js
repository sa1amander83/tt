// PromoAPI.validate
export const PromoAPI = {
  validate: (code, userId) =>
    fetch('/management/validate-promo/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
      },
      body: JSON.stringify({ code, user_id: userId })
    }).then(r => {
      if (!r.ok) throw new Error(r.statusText);
      return r.json();
    })
};