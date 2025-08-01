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
