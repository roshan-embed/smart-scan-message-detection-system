/**
 * SMART SCAM MESSAGE DETECTION SYSTEM
 * Authentication & Security Script (Client Validation & Password Meter)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Password Visibility Toggle
  const toggleBtns = document.querySelectorAll(".btn-toggle-password");
  toggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      if (!input) return;

      const isPassword = input.getAttribute("type") === "password";
      input.setAttribute("type", isPassword ? "text" : "password");

      // Update icon SVG
      btn.innerHTML = isPassword
        ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`;
    });
  });

  // Password Strength Evaluation for Registration & Password Change
  const pwdInput = document.getElementById("password_input");
  const meterBars = document.querySelectorAll(".meter-bar");
  const meterText = document.getElementById("meter_strength_text");
  
  const reqLength = document.getElementById("req_length");
  const reqLower = document.getElementById("req_lower");
  const reqUpper = document.getElementById("req_upper");
  const reqNumber = document.getElementById("req_number");
  const reqSpecial = document.getElementById("req_special");

  if (pwdInput && meterBars.length > 0) {
    pwdInput.addEventListener("input", () => {
      const val = pwdInput.value;
      const scores = evaluatePassword(val);
      updateMeterUI(scores);
    });
  }

  function evaluatePassword(pwd) {
    const hasLength = pwd.length >= 8;
    const hasLower = /[a-z]/.test(pwd);
    const hasUpper = /[A-Z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\-+=~`\[\]/]/.test(pwd);

    updateReqItem(reqLength, hasLength);
    updateReqItem(reqLower, hasLower);
    updateReqItem(reqUpper, hasUpper);
    updateReqItem(reqNumber, hasNumber);
    updateReqItem(reqSpecial, hasSpecial);

    let score = 0;
    if (hasLength) score++;
    if (hasLower && hasUpper) score++;
    if (hasNumber) score++;
    if (hasSpecial) score++;

    return { score, length: pwd.length };
  }

  function updateReqItem(el, isValid) {
    if (!el) return;
    if (isValid) {
      el.classList.add("valid");
    } else {
      el.classList.remove("valid");
    }
  }

  function updateMeterUI({ score, length }) {
    // Reset all bars
    meterBars.forEach(bar => {
      bar.className = "meter-bar";
    });

    if (length === 0) {
      if (meterText) meterText.textContent = "Password strength";
      return;
    }

    if (score <= 1) {
      meterBars[0].classList.add("active-weak");
      if (meterText) {
        meterText.textContent = "Weak (Unsafe)";
        meterText.style.color = "var(--danger)";
      }
    } else if (score === 2 || score === 3) {
      meterBars[0].classList.add("active-medium");
      meterBars[1].classList.add("active-medium");
      if (score === 3) meterBars[2].classList.add("active-medium");
      if (meterText) {
        meterText.textContent = score === 2 ? "Moderate" : "Good";
        meterText.style.color = "var(--warning-text)";
      }
    } else if (score === 4) {
      meterBars.forEach(bar => bar.classList.add("active-strong"));
      if (meterText) {
        meterText.textContent = "Strong (Optimal)";
        meterText.style.color = "var(--safe)";
      }
    }
  }

  // Quick Demo Account Autofill
  const fillBtns = document.querySelectorAll(".demo-btn-fill");
  fillBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const email = btn.getAttribute("data-email");
      const password = btn.getAttribute("data-password");
      const identifierInput = document.getElementById("identifier_input");
      const passwordInput = document.getElementById("password_input");

      if (identifierInput && passwordInput) {
        identifierInput.value = email;
        passwordInput.value = password;
        identifierInput.focus();
      }
    });
  });
});
