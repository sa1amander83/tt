export const formatDate = (date) => {
  if (!date || isNaN(new Date(date))) return '';
  const d = new Date(date);
  return d.toISOString().split('T')[0];
}

export function getMonday(date) {
  if (!date || isNaN(new Date(date))) return new Date();
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(d.setDate(diff));
}

export function getWeekInterval(date) {
    const startOfWeek = getMonday(date);
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 6); // конец недели (воскресенье)

    const startStr = startOfWeek.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });
    const endStr = endOfWeek.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });

    return `${startStr} - ${endStr}`;
}
export const addDays = (date, days) => {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
};

export const addMonths = (date, months) => {
  const d = new Date(date);
  d.setMonth(d.getMonth() + months);
  return d;
};