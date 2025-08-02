export const html = (strings, ...values) =>
  strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');

export const showLoader = () => $('#loader')?.classList.remove('hidden');
export const hideLoader = () => $('#loader')?.classList.add('hidden');

