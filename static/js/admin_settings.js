
        document.addEventListener('DOMContentLoaded', function() {
            // Mobile menu toggle
            const mobileMenuButton = document.getElementById('mobile-menu-button');
            const mobileMenu = document.getElementById('mobile-menu');

            if (mobileMenuButton && mobileMenu) {
                mobileMenuButton.addEventListener('click', function() {
                    mobileMenu.classList.toggle('hidden');
                });
            }

            // Tab switching functionality
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Get the tab to show
                    const tabToShow = this.getAttribute('data-tab');

                    // Remove active class from all buttons
                    tabButtons.forEach(btn => {
                        btn.classList.remove('border-green-500', 'text-green-600');
                        btn.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-2 border-gray-300');
                    });

                    // Add active class to clicked button
                    this.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-2 border-gray-300');
                    this.classList.add('border-green-500', 'text-green-600');

                    // Hide all tab contents
                    tabContents.forEach(content => {
                        content.classList.add('hidden');
                    });

                    // Show the selected tab content
                    document.getElementById('tab-' + tabToShow).classList.remove('hidden');
                });
            });

            // Holiday status change handler
            const holidayStatus = document.getElementById('holiday-status');
            const shortenedHours = document.getElementById('shortened-hours');

            if (holidayStatus && shortenedHours) {
                holidayStatus.addEventListener('change', function() {
                    if (this.value === 'shortened' || this.value === 'special') {
                        shortenedHours.classList.remove('hidden');
                    } else {
                        shortenedHours.classList.add('hidden');
                    }
                });
            }
        });
document.addEventListener('DOMContentLoaded', function() {
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
    holidayStatus.addEventListener('change', function() {
      holidayHoursFields.classList.toggle('hidden', !['shortened', 'special'].includes(this.value));
    });
  }
});


document.addEventListener('DOMContentLoaded', function() {
  // Показываем/скрываем поля времени для праздничных дней
  const holidayStatus = document.getElementById('id_status');
  const holidayHoursFields = document.getElementById('holiday-hours-fields');

  if (holidayStatus && holidayHoursFields) {
    holidayStatus.addEventListener('change', function() {
      if (this.value === 'shortened' || this.value === 'special') {
        holidayHoursFields.classList.remove('hidden');
      } else {
        holidayHoursFields.classList.add('hidden');
      }
    });
  }

  // Инициализация flatpickr для выбора даты
  const dateInput = document.getElementById('id_date');
  if (dateInput) {
    flatpickr(dateInput, {
      dateFormat: "d.m.Y",
      allowInput: true,
      locale: "ru"
    });
  }
});