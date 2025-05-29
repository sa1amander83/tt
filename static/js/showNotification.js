
        window.showNotification = function (message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center transform transition-all duration-300 ${
                type === 'success' ? 'bg-green-500' : 'bg-red-500'
            }`;

            notification.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${
                type === 'success' ? 'M5 13l4 4L19 7' : 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            }"></path>
        </svg>
        ${message}
    `;

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.classList.remove('translate-x-full', 'opacity-0');
            }, 10);

            setTimeout(() => {
                notification.classList.add('opacity-0', 'translate-x-full');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 5000);
        }