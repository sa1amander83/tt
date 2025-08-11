import { $ } from '../../utils/dom.js';

const priceStrategies = {
  30: (p) => p.halfHour,
  60: (p) => p.hour,
  other: (p, mins) => {
    const h = Math.floor(mins / 60);
    const half = Math.ceil((mins % 60) / 30);
    return h * p.hour + half * p.halfHour;
  }
};

export function calcTableCost(mins, price) {
  return (priceStrategies[mins] || priceStrategies.other)(price, mins);
}

export function updateCost(store) {
  const { rates } = store.get();
  const duration = Number($('#booking-duration').value);
  const tableId = $('#booking-table').value;
  const table = rates.tables?.find(t => t.id === Number(tableId));
  if (!table) return;

  const tableCost = calcTableCost(duration, table.prices);
  const equipmentCost = 0; // TODO
  const discount = store.get().promoApplied ? 0.1 : 0;
  const total = Math.round((tableCost + equipmentCost) * (1 - discount));

  $('#tariff-table-cost').textContent = `${tableCost} ₽`;
  $('#tariff-equipment-cost').textContent = `${equipmentCost} ₽`;
  $('#tariff-total-cost').textContent = `${total} ₽`;
}