/**
 * SMART SCAM MESSAGE DETECTION SYSTEM
 * Global Client Script
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lucide icons if loaded
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Auto-dismiss alert messages after 6 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      });
    }

    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.transition = "opacity 0.3s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 300);
      }
    }, 6000);
  });
});
