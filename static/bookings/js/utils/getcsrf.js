export const getCSRFToken = document.cookie
  .split('; ')
  .find(r => r.startsWith('csrftoken='))
  ?.split('=')[1] || '';