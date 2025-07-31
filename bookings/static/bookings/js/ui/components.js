export const html = (strings, ...values) =>
  strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');

export const showLoader = () => $('#loader')?.classList.remove('hidden');
export const hideLoader = () => $('#loader')?.classList.add('hidden');

export const showNotification = (text, type = 'info') => {
  const el = $('#notification');
  if (!el) return alert(text);
  el.textContent = text;
  el.className = `notification ${type}`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 3000);
};