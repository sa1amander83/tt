export const formatDate = (d) => {
  const dt = new Date(d); // клон
  dt.setHours(0, 0, 0, 0); // чтобы часовой пояс не сдвинул дату
  const yyyy = dt.getFullYear();
  const mm = String(dt.getMonth() + 1).padStart(2, '0');
  const dd = String(dt.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export function getMonday(d) {
  const dt = new Date(d);
  dt.setHours(0, 0, 0, 0);
  const day = dt.getDay(); // 0 = вс
  const diff = (day === 0 ? -6 : 1) - day;
  dt.setDate(dt.getDate() + diff);
  return dt;
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