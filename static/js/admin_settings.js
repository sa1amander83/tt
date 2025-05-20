//общие функции админки

document.addEventListener('DOMContentLoaded', function () {
    // Инициализация flatpickr для всех модалок
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    dateInputs.forEach(input => {
        flatpickr(input, {
            dateFormat: "d.m.Y",
            allowInput: true,
            locale: "ru"
        });
    });

    // Обработка статуса праздника
    const holidayStatus = document.getElementById('id_status');
    const holidayHoursFields = document.getElementById('holiday-hours-fields');

    if (holidayStatus && holidayHoursFields) {
        holidayStatus.addEventListener('change', function () {
            holidayHoursFields.classList.toggle('hidden', !['shortened', 'special'].includes(this.value));
        });
    }
});

//*
// document.addEventListener('DOMContentLoaded', function() {
//   // Показываем/скрываем поля времени для праздничных дней
//   const holidayStatus = document.getElementById('id_status');
//   const holidayHoursFields = document.getElementById('holiday-hours-fields');
//
//   if (holidayStatus && holidayHoursFields) {
//     holidayStatus.addEventListener('change', function() {
//       if (this.value === 'shortened' || this.value === 'special') {
//         holidayHoursFields.classList.remove('hidden');
//       } else {
//         holidayHoursFields.classList.add('hidden');
//       }
//     });
//   }
// Инициализация flatpickr для выбора даты
const dateInput = document.getElementById('id_date');
if (dateInput) {
    flatpickr(dateInput, {
        dateFormat: "d.m.Y",
        allowInput: true,
        locale: "ru"
    });
}


document.querySelectorAll('input[type="time"]').forEach(input => {
    flatpickr(input, {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        minuteIncrement: 30,
        locale: "ru"
    });
});

function showNotification(message, type) {
    const notification = document.createElement('div');

    // Установка базовых классов
    notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded shadow-lg text-white transition-opacity duration-500 opacity-100 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;

    // Установка текста
    notification.textContent = message;

    // Добавление в DOM
    document.body.appendChild(notification);

    // Исчезновение (плавно)
    setTimeout(() => {
        notification.style.opacity = '0'; // исчезает плавно
    }, 2500); // 2.5 сек виден

    // Полное удаление
    setTimeout(() => {
        notification.remove();
    }, 3000); // через 3 сек удаляется
}
