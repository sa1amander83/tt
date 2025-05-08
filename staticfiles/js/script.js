// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Form submissions
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
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
                fullname: document.getElementById('user-name').value,
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




// Loyalty Program Display Logic
document.addEventListener("DOMContentLoaded", () => {
  // This would normally be fetched from the server
  const mockUserLoyalty = {
    level: "START", // START, SILVER, GOLD, PLATINUM
    points: 150,
    discount: 0,
  }

  const levelThresholds = {
    START: 0,
    SILVER: 1000,
    GOLD: 5000,
    PLATINUM: 10000,
  }

  const levelDiscounts = {
    START: 0,
    SILVER: 5,
    GOLD: 10,
    PLATINUM: 15,
  }

  // Update loyalty display on profile page
  function updateLoyaltyDisplay() {
    const levelElements = document.querySelectorAll(".current-level")
    const discountElements = document.querySelectorAll(".current-discount")
    const pointsElements = document.querySelectorAll(".current-points")
    const progressBars = document.querySelectorAll(".progress-bar")
    const pointsToNextElements = document.querySelectorAll(".points-to-next-level")

    // Hide all badges first
    document.querySelectorAll(".basic-badge, .silver-badge, .gold-badge, .platinum-badge").forEach((badge) => {
      badge.classList.add("hidden")
    })

    // Show the appropriate badge
    let badgeClass = ""
    switch (mockUserLoyalty.level) {
      case "PLATINUM":
        badgeClass = ".platinum-badge"
        break
      case "GOLD":
        badgeClass = ".gold-badge"
        break
      case "SILVER":
        badgeClass = ".silver-badge"
        break
      default:
        badgeClass = ".basic-badge"
    }

    document.querySelectorAll(badgeClass).forEach((badge) => {
      badge.classList.remove("hidden")
    })

    // Update text elements
    let levelName = ""
    switch (mockUserLoyalty.level) {
      case "PLATINUM":
        levelName = "Платиновый"
        break
      case "GOLD":
        levelName = "Золотой"
        break
      case "SILVER":
        levelName = "Серебряный"
        break
      default:
        levelName = "Старт"
    }

    levelElements.forEach((el) => {
      el.textContent = levelName
    })

    discountElements.forEach((el) => {
      el.textContent = `${levelDiscounts[mockUserLoyalty.level]}%`
    })

    pointsElements.forEach((el) => {
      el.textContent = mockUserLoyalty.points
    })

    // Calculate progress to next level
    let nextLevel = ""
    let pointsToNext = 0

    switch (mockUserLoyalty.level) {
      case "START":
        nextLevel = "SILVER"
        break
      case "SILVER":
        nextLevel = "GOLD"
        break
      case "GOLD":
        nextLevel = "PLATINUM"
        break
      case "PLATINUM":
        nextLevel = "PLATINUM" // Already at max
        break
    }

    if (nextLevel !== mockUserLoyalty.level) {
      pointsToNext = levelThresholds[nextLevel] - mockUserLoyalty.points

      // Calculate progress percentage
      const currentThreshold = levelThresholds[mockUserLoyalty.level]
      const nextThreshold = levelThresholds[nextLevel]
      const range = nextThreshold - currentThreshold
      const progress = mockUserLoyalty.points - currentThreshold
      const percentage = Math.min(100, Math.max(0, (progress / range) * 100))

      progressBars.forEach((bar) => {
        bar.style.width = `${percentage}%`
      })
    } else {
      // At max level
      pointsToNext = 0
      progressBars.forEach((bar) => {
        bar.style.width = "100%"
      })
    }

    pointsToNextElements.forEach((el) => {
      el.textContent = pointsToNext
    })

    // Update level markers
    document.querySelectorAll(".level-marker").forEach((marker, index) => {
      const levels = ["START", "SILVER", "GOLD", "PLATINUM"]
      const level = levels[index]

      // Reset all markers
      marker.querySelector("div").className = "h-1 bg-gray-300 rounded"

      // Highlight current and previous levels
      if (levelThresholds[level] <= mockUserLoyalty.points) {
        marker.querySelector("div").className = "h-1 bg-green-600 rounded"
      }
    })
  }

  // Update booking modal to show loyalty discount
  function updateBookingModal() {
    const discountElement = document.querySelector(".pt-4 .mb-2:nth-child(3) .font-medium:last-child")
    const totalElement = document.querySelector(".pt-4 .font-medium:last-child")

    if (discountElement && totalElement) {
      const bookingDuration = document.getElementById("booking-duration")
      const bookingEquipment = document.getElementById("booking-equipment")
      const tableSelect = document.getElementById("booking-table")

      if (bookingDuration && bookingEquipment && tableSelect) {
        const duration = Number.parseInt(bookingDuration.value)
        const equipmentRental = bookingEquipment.checked ? 200 : 0
        const tableOption = tableSelect.options[tableSelect.selectedIndex]
        const tableType = tableOption.text.includes("Профессиональный") ? "pro" : "standard"
        const hourlyRate = tableType === "pro" ? 500 : 400
        const tableRental = hourlyRate * duration

        // Calculate discount
        const discount = levelDiscounts[mockUserLoyalty.level]
        const discountAmount = Math.round((tableRental * discount) / 100)
        const total = tableRental + equipmentRental - discountAmount

        // Update discount text
        const discountText = document.querySelector(".pt-4 .mb-2:nth-child(3) .text-sm.font-medium.text-gray-700")
        if (discountText) {
          discountText.textContent = `Скидка по программе лояльности (${discount}%):`
        }

        discountElement.textContent = `-${discountAmount} ₽`
        totalElement.textContent = `${total} ₽`
      }
    }
  }

  // Call the update functions when the page loads
  if (document.querySelector(".current-level")) {
    updateLoyaltyDisplay()
  }

  // Update booking modal when values change
  const bookingDuration = document.getElementById("booking-duration")
  const bookingEquipment = document.getElementById("booking-equipment")
  const bookingTable = document.getElementById("booking-table")

  if (bookingDuration) {
    bookingDuration.addEventListener("change", updateBookingModal)
  }

  if (bookingEquipment) {
    bookingEquipment.addEventListener("change", updateBookingModal)
  }

  if (bookingTable) {
    bookingTable.addEventListener("change", updateBookingModal)
  }

  // Initial update for booking modal
  if (document.getElementById("booking-modal")) {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (
          mutation.attributeName === "class" &&
          !document.getElementById("booking-modal").classList.contains("hidden")
        ) {
          updateBookingModal()
        }
      })
    })

    observer.observe(document.getElementById("booking-modal"), {
      attributes: true,
    })
  }
})
})
