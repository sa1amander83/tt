let loaderStartTime = null;

function showLoader() {
    loaderStartTime = Date.now();

    document.getElementById('loader').style.display = 'flex';
}

function hideLoader() {
    const elapsed = Date.now() - loaderStartTime;

    const delay = Math.max(0, 1000 - elapsed);  // гарантируем минимум 2 секунды

    setTimeout(() => {
        document.getElementById('loader').style.display = 'none';
    }, delay);
}