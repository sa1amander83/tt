// Mobile menu toggle - обновлённая версия
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = mobileMenuButton.querySelector('i');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            // Переключаем видимость меню
            mobileMenu.classList.toggle('hidden');
            mobileMenu.classList.toggle('md:hidden');
            mobileMenu.classList.toggle('block');
                document.body.classList.remove('hidden');

            // Меняем иконку
            menuIcon.classList.toggle('fa-bars');
            menuIcon.classList.toggle('fa-times');

            // Блокируем/разблокируем прокрутку страницы
            document.body.classList.toggle('overflow-hidden');
        });

        // Закрытие меню при клике на пункт
        const menuLinks = document.querySelectorAll('#mobile-menu a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('block');
                menuIcon.classList.add('fa-bars');
                menuIcon.classList.remove('fa-times');
                document.body.classList.remove('overflow-hidden');
            });
        });
    }
});
// Function to format date
function formatDate(dateString) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    return new Date(dateString).toLocaleDateString('ru-RU', options);
}



const profileForm = document.getElementById('profile-form');
if (profileForm) {
    // Load user data
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData) {
        // Update displayed user info in sidebar
        const userNameElement = document.getElementById('user-name');
        const userEmailElement = document.getElementById('user-email');

        if (userNameElement) userNameElement.textContent = userData.fullname || '';
        if (userEmailElement) userEmailElement.textContent = userData.email || '';

        // Fill form fields
        const fullnameInput = document.getElementById('fullname');
        const emailInput = document.getElementById('email');
        const phoneInput = document.getElementById('phone');
        const levelSelect = document.getElementById('level');

        if (fullnameInput) fullnameInput.value = userData.fullname || '';
        if (emailInput) emailInput.value = userData.email || '';
        if (phoneInput) phoneInput.value = userData.phone || '';
        if (levelSelect) levelSelect.value = userData.level || 'beginner';
    }
        profileForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Get form values
        const fullname = document.getElementById('fullname').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const level = document.getElementById('level').value;

        // Update user data
        const userData = JSON.parse(localStorage.getItem('user')) || {};
        userData.fullname = fullname;
        userData.email = email;
        userData.phone = phone;
        userData.level = level;

        localStorage.setItem('user', JSON.stringify(userData));

        // Update displayed name and email in sidebar
        const userNameElement = document.getElementById('user-name');
        const userEmailElement = document.getElementById('user-email');
        if (userNameElement) userNameElement.textContent = fullname;
        if (userEmailElement) userEmailElement.textContent = email;

        alert('Профиль успешно обновлен');
    });
}
