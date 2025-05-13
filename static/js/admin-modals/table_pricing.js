  // Unified modal functions
  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}Backdrop`);
    const content = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}ModalContent`);

    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');

    // Trigger animations
    setTimeout(() => {
      backdrop.classList.add('opacity-100');
      content.classList.add('opacity-100', 'translate-y-0');
    }, 10);
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}Backdrop`);
    const content = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}ModalContent`);

    backdrop.classList.remove('opacity-100');
    content.classList.remove('opacity-100', 'translate-y-0');

    setTimeout(() => {
      modal.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }, 300);
  }

  // Initialize modals
  document.addEventListener('DOMContentLoaded', () => {
    const modals = ['addPricingPlanModal', 'addSpecialOfferModal', 'addTableTypePricingModal'];
    modals.forEach(modalId => {
      const backdrop = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}Backdrop`);
      const content = document.getElementById(`${modalId.replace('add', '').replace('Modal', '')}ModalContent`);

      if (backdrop && content) {
        backdrop.classList.add('opacity-0');
        content.classList.add('opacity-0', 'translate-y-10');
      }
    });
  });

  // Form submission handlers
  async function savePricingPlan() {
    const form = document.getElementById('pricingPlanForm');
    const saveBtn = document.querySelector('#addPricingPlanModal button[onclick="savePricingPlan()"]');

    if (form.checkValidity()) {
      try {
        // Show loading state
        saveBtn.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Сохранение...
        `;
        saveBtn.disabled = true;

        // Here would be your actual API call
        // const response = await fetch('/api/pricing-plans', { method: 'POST', body: new FormData(form) });

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Show success and close
        showNotification('Тарифный план успешно создан!', 'success');
        closeModal('addPricingPlanModal');
        form.reset();
      } catch (error) {
        showNotification('Ошибка при сохранении: ' + error.message, 'error');
      } finally {
        saveBtn.innerHTML = 'Сохранить тариф';
        saveBtn.disabled = false;
      }
    } else {
      form.reportValidity();
    }
  }

  // Similar functions for other modals...

  // Notification system
  function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center transform translate-x-full opacity-0 transition-all duration-300 ${
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


  }
