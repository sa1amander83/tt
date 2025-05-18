// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Form submissions
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                alert('Пароли не совпадают');
                return;
            }

            // In a real app, you would send this data to a server
            // For demo purposes, we'll store in localStorage
            const userData = {
                fullname: document.getElementById('user_name').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                password: password, // In a real app, NEVER store passwords in plain text
                level: 'beginner',
                registeredAt: new Date().toISOString()
            };

            localStorage.setItem('user', JSON.stringify(userData));
            alert('Регистрация успешна! Теперь вы можете войти в систему.');
            window.location.href = 'login.html';
        });
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // In a real app, you would validate credentials against a server
            // For demo purposes, we'll check localStorage
            const userData = JSON.parse(localStorage.getItem('user'));

            if (userData && userData.email === email && userData.password === password) {
                localStorage.setItem('isLoggedIn', 'true');
                window.location.href = 'profile.html';
            } else {
                alert('Неверный email или пароль');
            }
        });
    }

    const recoverForm = document.getElementById('recover-form');
    if (recoverForm) {
        recoverForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;

            // In a real app, you would send a recovery email
            alert(`Инструкции по восстановлению пароля отправлены на ${email}`);
            window.location.href = 'login.html';
        });
    }

    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        // Load user data
        const userData = JSON.parse(localStorage.getItem('user'));
        if (userData) {
            document.getElementById('user_name').textContent = userData.fullname;
            document.getElementById('user-email').textContent = userData.email;

            document.getElementById('user_name').value = userData.fullname;
            document.getElementById('email').value = userData.email;
            document.getElementById('phone').value = userData.phone;
        }

        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Update user data
            userData.fullname = document.getElementById('user_name').value;
            userData.email = document.getElementById('email').value;
            userData.phone = document.getElementById('phone').value;
            userData.level = document.getElementById('level').value;

            localStorage.setItem('user', JSON.stringify(userData));

            // Update displayed name and email
            document.getElementById('user_name').textContent = userData.fullname;
            document.getElementById('user-email').textContent = userData.email;

            alert('Профиль успешно обновлен');
        });
    }

    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmNewPassword = document.getElementById('confirm-new-password').value;

            // Get user data
            const userData = JSON.parse(localStorage.getItem('user'));

            if (!userData || userData.password !== currentPassword) {
                alert('Текущий пароль неверен');
                return;
            }

            if (newPassword !== confirmNewPassword) {
                alert('Новые пароли не совпадают');
                return;
            }

            // Update password
            userData.password = newPassword;
            localStorage.setItem('user', JSON.stringify(userData));

            alert('Пароль успешно изменен');

            // Clear form
            passwordForm.reset();
        });
    }

    // Check if user is logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const publicPages = ['index.html', 'login.html', 'register.html', 'recover.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // Redirect logic
    if (!isLoggedIn && !publicPages.includes(currentPage)) {
        // Redirect to login if trying to access protected pages while not logged in
        window.location.href = 'login.html';
    }

    // Logout functionality
    const logoutLinks = document.querySelectorAll('#logout-link, #mobile-logout-link');
    logoutLinks.forEach(link => {
        if (link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.setItem('isLoggedIn', 'false');
                window.location.href = 'login.html';
            });
        }
    });
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


