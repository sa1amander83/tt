export const csrfToken = document.cookie
  .split('; ')
  .find(r => r.startsWith('csrftoken='))
  ?.split('=')[1] || '';