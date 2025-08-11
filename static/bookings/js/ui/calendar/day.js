import {html} from '../components.js';
import {BookingModal} from "../bookingModal/index.js";
import {BookingAPI} from "../../api/booking.js";


export const DayView = {
    render(data, store) {
        if (!data.is_working_day)
            return html`
                <div class="p-8 text-center">Выходной день</div>`;

        const rows = data.time_slots.map(time => {
            const cells = data.tables.map(t => this.slotCell(data, t, time, store));
            return html`
                <div class="flex border-b">
                    <div class="w-24 p-2 text-right">${time}</div>
                    <div class="flex-1 grid grid-cols-${data.tables.length} gap-px">
                        ${cells.join('')}
                    </div>
                </div>`;
        }).join('');

        return html`
            <div class="overflow-hidden border rounded">
                ${this.header(data.tables)}
                ${rows}
            </div>`;
    },

    header(tables) {
        return html`
            <div class="flex border-b bg-gray-50">
                <div class="w-24 p-2">Время</div>
                ${tables.map(t => html`
                    <div class="flex-1 p-2 text-center">Стол #${t.number}</div>`).join('')}
            </div>`;
    },

slotCell(data, table, time, store) {
    const slot = data.day_schedule[table.number]?.[time] || {};
    const state = store.get();
    const user = state.user;

    const now = new Date();
    const slotStart = new Date(`${data.date}T${time}`);
    const durationMinutes = slot.duration || 30;
    const slotEnd = new Date(slotStart.getTime() + durationMinutes * 60000);

    const status = slot.status || 'available';
    const username = slot.user?.name || '';
    const bookingId = slot.booking_id || null;

    let cls = '';
    let textTop = '';
    let textBottom = '';
    let clickable = false;

    const userId = user?.user_id || null;
    const isUserBooking =
        user && !user.is_staff &&
        slot.user && slot.user.id === userId &&
        ['pending', 'paid', 'completed', 'processing'].includes(status);

    const minutesSinceStart = (now - slotStart) / 60000;
    const isWithin5Minutes = minutesSinceStart >= 0 && minutesSinceStart <= 5;
    const isSlotPast = now >= slotEnd;

    if (isUserBooking) {
        cls = 'bg-red-900 text-white text-xl rounded-xl ring-4 ring-inset ring-amber-950';
        textTop = 'Ваша бронь';
        switch(status) {
            case 'processing': textBottom = 'Идёт сейчас'; break;
            case 'pending': textBottom = 'Ожидает оплаты'; break;
            case 'paid': textBottom = 'Оплачено'; break;
            case 'completed': textBottom = 'Завершено'; break;
        }
        clickable = false;
    } else if (user?.is_staff) {
        if (isSlotPast) {
            switch (status) {
                case 'completed':
                    cls = 'bg-green-100 text-green-800 rounded-xl';
                    textBottom = 'Завершено';
                    textTop = username;
                    break;
                case 'cancelled':
                    cls = 'bg-red-100 text-red-800 rounded-xl';
                    textBottom = 'Отменено';
                    textTop = username;
                    break;
                case 'expired':
                    cls = 'bg-gray-300 text-gray-900 rounded-xl';
                    textBottom = 'Просрочено';
                    textTop = username || '';
                    break;
                default:
                    cls = 'bg-gray-200 text-gray-800 rounded-xl';
                    textBottom = '—';
                    textTop = username || '';
            }
        } else {
            switch (status) {
                case 'processing':
                    cls = 'bg-blue-500 text-white rounded-xl';
                    textBottom = 'Идёт сейчас';
                    textTop = username;
                    break;
                case 'pending':
                    cls = 'bg-yellow-500 text-white rounded-xl';
                    textBottom = 'Ожидает оплаты';
                    clickable = true;
                    textTop = username;
                    break;
                case 'paid':
                    cls = 'bg-red-500 text-white text-xl font-bold rounded-xl';
                    textBottom = 'Оплачено';
                    textTop = username;
                    break;
                case 'returned':
                    cls = 'bg-purple-200 text-purple-900 rounded-xl';
                    textBottom = 'Оплата возвращена';
                    textTop = username;
                    break;
                case 'expired':
                    if (now < slotStart) {
                        cls = 'bg-green-500 text-white rounded-xl';
                        textBottom = 'Свободен';
                        clickable = true;
                        textTop = '';
                    } else {
                        cls = 'bg-gray-300 text-gray-900 rounded-xl';
                        textBottom = 'Просрочено';
                        textTop = username || '';
                    }
                    break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';
                    textBottom = 'Свободен';
                    clickable = true;
                    textTop = '';
            }
        }
    } else {
        if (status === 'processing') {
            cls = 'bg-blue-500 text-white rounded-xl';
            textBottom = 'Идёт сейчас';
            textTop = '';
        } else if (isSlotPast) {
            if (status === 'completed') {
                cls = 'bg-green-100 text-green-800 rounded-xl';
                textBottom = 'Завершено';
                textTop = '';
            } else {
                cls = 'bg-gray-200 text-gray-800 rounded-xl';
                textBottom = '—';
                textTop = '';
            }
        } else {
            switch (status) {
                case 'pending':
                    cls = 'bg-yellow-500 text-white rounded-xl';
                    textBottom = 'Ожидает оплаты';
                    clickable = true;
                    textTop = '';
                    break;
                case 'paid':
                    cls = 'bg-red-300 text-white rounded-xl';
                    textBottom = 'Занят';
                    textTop = '';
                    break;
                case 'expired':
                    if (now < slotStart) {
                        cls = 'bg-green-500 text-white rounded-xl';
                        textBottom = 'Свободен';
                        clickable = true;
                        textTop = '';
                    } else {
                        cls = 'bg-gray-200 text-gray-800 rounded-xl';
                        textBottom = '—';
                        textTop = '';
                    }
                    break;
                default:
                    cls = 'bg-green-500 text-white rounded-xl';
                    textBottom = 'Свободен';
                    clickable = true;
                    textTop = '';
            }
        }
    }

    if (!clickable && status === 'available' && isWithin5Minutes) {
        clickable = true;
    }

    // Новый обработчик onClick
    let onClick = null;

    if (status === 'expired' && clickable || status === 'cancelled' && clickable || status === 'returned' && clickable) {
        onClick = `openCreateBooking({date:'${data.date}',time:'${time}',tableId:${table.number}})`;
    } else if (bookingId && user?.is_staff) {
        onClick = `openBookingDetail(${bookingId})`;
    } else if (clickable) {
        onClick = `openCreateBooking({date:'${data.date}',time:'${time}',tableId:${table.number}})`;
    }

    return html`
        <div class="p-px">
            <div
                class="flex flex-col items-center justify-center h-12 w-full leading-tight text-center ${cls} ${onClick ? 'cursor-pointer hover:opacity-90' : ''}"
                ${onClick ? `onclick="${onClick}"` : ''}
            >
                ${textTop ? `<div class="text-xs">${textTop}</div>` : ''}
                ${textBottom ? `<div class="text-xs">${textBottom}</div>` : ''}
            </div>
        </div>
    `;
}
};
window.openCreateBooking = ({date, time, tableId}) => {
    // если BookingModal – ES-модуль, используйте импорт
    // import('/static/js/modals/bookingModal.js').then(m => m.BookingModal.open(...))
    BookingModal.open({date, time, tableId});
};


window.openBookingDetail = async (bookingId) => {
    const modal = document.getElementById('detail-booking-modal');
    if (!modal) return;

    modal.querySelector('.modal-content').innerHTML = `
    <div class="flex justify-center items-center h-full">
      <div class="bg-white rounded-lg shadow-lg max-w-3xl w-full p-6 relative">
        <p class="text-center text-gray-500">Загрузка...</p>
      </div>
    </div>
  `;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    try {
        const res = await fetch(`/bookings/api/booking_detail_by_id/${bookingId}/`, {credentials: 'include'});
        if (!res.ok) throw new Error('status ' + res.status);
        const d = await res.json(); // d = data

        modal.querySelector('.modal-content').innerHTML = `
      <div class="max-w-3xl w-full bg-white rounded-lg shadow-lg p-6 overflow-auto max-h-[80vh]">
        <h2 class="text-2xl font-bold mb-6 border-b pb-2">Бронирование #${d.bookingId}</h2>

        <table class="w-full text-sm text-gray-700">
          <tbody>
            <tr class="border-b"><td class="font-semibold w-1/3 py-2">Пользователь:</td><td class="py-2">${d.userName}</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Статус:</td><td class="py-2">${d.status}</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Дата / время:</td><td class="py-2">${new Date(d.start_time).toLocaleString()} – ${new Date(d.end_time).toLocaleString()}</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Стол:</td><td class="py-2">№ ${d.table_number}</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Участников:</td><td class="py-2">${d.participants} ${d.is_group ? '(группа)' : ''}</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Базовая цена:</td><td class="py-2">${d.base_price} ₽</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Оборудование:</td><td class="py-2">${d.equipment_price} ₽</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Промокод (-${d.promo_code_discount_percent}%):</td><td class="py-2">${d.promo_code_discount_percent}%</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Спец-скидка (-${d.special_offer_discount_percent}%):</td><td class="py-2">${d.special_offer_discount_percent}%</td></tr>
            <tr class="border-b"><td class="font-semibold py-2">Лояльность (-${d.loyalty_discount_percent}%):</td><td class="py-2">${d.loyalty_discount_percent}%</td></tr>
            <tr class="border-b"><td class="font-semibold py-2 text-lg">Итого:</td><td class="py-2 text-lg font-bold">${d.total_price} ₽</td></tr>
            ${d.notes ? `<tr><td class="font-semibold py-2">Примечания:</td><td class="py-2">${d.notes}</td></tr>` : ''}
          </tbody>
        </table>

  ${d.equipment.length ? `
  <h3 class="mt-4 font-semibold">Оборудование:</h3>
  <ul class="list-disc list-inside">
    ${d.equipment.map(e => `<li>${e.name} – ${e.quantity} шт</li>`).join('')}
  </ul>` : ''}

  <div class="mt-6 flex justify-end space-x-3">
    <button class="px-4 py-2 bg-gray-200 rounded" onclick="closeModal('detail-booking-modal')">Закрыть</button>
    ${
           (d.status === 'pending' || d.status === 'Ожидает оплаты')
                ? `<button class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600" onclick="cancelBooking(${d.bookingId})">Отменить</button>
         <button class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600" onclick="payBooking(${d.bookingId})">Оплатить</button>`
                : ''
        }
  </div>`
    } catch {
        modal.querySelector('.modal-content').innerHTML = `
      <div class="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
        <p class="text-red-600 font-semibold text-center">Ошибка загрузки данных.</p>
        <div class="flex justify-center mt-4">
          <button
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded transition"
            onclick="closeModal('detail-booking-modal')"
          >
            Закрыть
          </button>
        </div>
      </div>
    `;
    }
};

window.closeModal = () => {
    const modal = document.getElementById("detail-booking-modal");
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.style.overflow = 'auto';
};


window.payBooking = async (bookingId) => {
  console.log('payBooking: bookingId =', bookingId);

  if (!bookingId) {
    showNotification('Не передан ID брони', 'error');
    return;
  }

  try {
    const { payment_url, status, confirmation_url } = await BookingAPI.payment(bookingId);

    if (status === 'paid') {
      showNotification('Уже оплачено', 'success');
    } else if (payment_url) {
      window.open(payment_url, '_blank');
    } else if (confirmation_url) {
      window.open(confirmation_url, '_blank');
    } else {
      showNotification('Нет ссылки на оплату', 'error');
    }

    // Закрываем модалку
    closeModal('detail-booking-modal');

    // Пытаемся обновить только таблицу бронирований
    try {
      // Путь поправь, если нужно
      const mod = await import('../userBookings.js');
      const UserBookings = mod.UserBookings || mod.default;
      if (UserBookings && typeof UserBookings.render === 'function') {
        // Дополнительная проверка — store и контейнер
        if (!UserBookings.store) {
          console.warn('UserBookings.store не инициализирован. Попытка вызвать render всё равно.');
        }
        await UserBookings.render();
        return; // успешно обновили — не дергаем календарь
      } else {
        console.warn('UserBookings не экспортирован корректно или не имеет render()');
      }
    } catch (err) {
      console.warn('Не удалось импортировать или выполнить UserBookings.render():', err);
    }

    // fallback: обновляем календарь, если таблицу обновить не получилось
    if (window.CalendarUI && typeof CalendarUI.render === 'function') {
      await CalendarUI.render();
    } else {
      console.warn('Ни UserBookings, ни CalendarUI недоступны для обновления.');
    }

  } catch (e) {
    console.error('Ошибка payBooking:', e);
    showNotification('Не удалось начать оплату', 'error');
  }
};




window.cancelBooking = async (bookingId) => {
  if (!confirm('Вы уверены, что хотите отменить бронирование?')) return;
  try {
    const response = await fetch(`/bookings/api/cancel/${bookingId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    });
    const result = await response.json();
    if (result.success) {
      showNotification('Бронирование успешно отменено', 'success');
      closeModal('detail-booking-modal');
      await UserBookings.render(); // 🔹 просто обновляем таблицу
    } else {
      throw new Error(result.error || 'Неизвестная ошибка');
    }
  } catch (error) {
    console.error('Ошибка отмены бронирования:', error);
    showNotification(`Ошибка: ${error.message}`, 'error');
  }
};