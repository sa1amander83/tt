import { $ } from '../utils/dom.js';

export const PromoAPI = {
  validate: async (code, userId) => {
    try {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
      if (!csrfToken) {
        console.error('CSRF token not found');
        throw new Error('Security error');
      }

      const response = await fetch('/management/validate-promo/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          code: code,
          user_id: userId
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server responded with ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Promo validation failed:', error);
      throw error;
    }
  }
};

export async function applyPromoCodeToBooking(store) {
  const input = $('#promo-code');
  const msg = $('#promo-code-message');
  const userId = window.CURRENT_USER_ID || null;

  if (!input || !msg) {
    console.error('Required elements not found');
    return false;
  }

  const code = input.value.trim();
  if (!code) {
    msg.textContent = 'Please enter a promo code';
    msg.className = 'text-xs text-red-600';
    msg.classList.remove('hidden');
    return false;
  }

  try {
    const res = await PromoAPI.validate(code, userId);

    store.set({
      promoCode: res,
      promoApplied: res.valid
    });

    if (res.valid) {
      msg.textContent = res.description || 'Promo code applied successfully';
      msg.className = 'text-xs text-green-600';
    } else {
      msg.textContent = res.error || 'Invalid promo code';
      msg.className = 'text-xs text-red-600';
    }
    msg.classList.remove('hidden');

    return res.valid;
  } catch (err) {
    console.error('Promo application error:', err);
    msg.textContent = err.message || 'Error validating promo code';
    msg.className = 'text-xs text-red-600';
    msg.classList.remove('hidden');
    return false;
  }
}