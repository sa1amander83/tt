
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
                        btn.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
                    });

                    // Add active class to clicked button
                    this.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
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
