/**
 * SMART SCAM MESSAGE DETECTION SYSTEM
 * Module 2: Smart Message Scanner Client Logic
 * Handles real-time character counting, tab switching, clearing, and sample loaders.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabBtns = document.querySelectorAll(".channel-tab-btn");
  const messageTypeInput = document.getElementById("message_type_input");
  const textarea = document.getElementById("message_content_input");
  const senderFieldContainer = document.getElementById("sender_field_container");
  const senderInput = document.getElementById("sender_info_input");
  const senderLabel = document.getElementById("sender_info_label");
  const emailSubjectContainer = document.getElementById("email_subject_container");
  const subjectInput = document.getElementById("subject_input");

  const charCountEl = document.getElementById("counter_char_count");
  const wordCountEl = document.getElementById("counter_word_count");
  const smsSegmentsContainer = document.getElementById("sms_segments_container");
  const smsSegmentsEl = document.getElementById("counter_sms_segments");
  const progressFill = document.getElementById("counter_progress_fill");

  const clearBtn = document.getElementById("btn_clear_message");
  const sampleBtn = document.getElementById("btn_load_sample");

  const MAX_CHARS = 10000;

  // Placeholder texts per channel
  const PLACEHOLDERS = {
    sms: "Paste raw SMS text here... e.g.\n'URGENT: Your account has been temporarily suspended. Verify your identity at http://bank-secure-update.xyz to avoid closure.'",
    whatsapp: "Paste WhatsApp message or chat export here... e.g.\n'*Forwarded many times*\nCongratulations! You have been selected for an online remote job earning $500 daily. Contact our hiring manager on Telegram: http://t.me/hr_job_recruitment'",
    email: "Paste the complete email body here... e.g.\n'Dear Customer, We detected an unauthorized sign-in attempt from IP 194.26.29.112. Click here to confirm credentials immediately: http://account-verification-portal.com'"
  };

  // 1. Channel Tab Switching
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const channel = btn.getAttribute("data-channel");
      if (messageTypeInput) messageTypeInput.value = channel;

      // Adjust channel-specific inputs
      if (channel === "email") {
        if (emailSubjectContainer) emailSubjectContainer.style.display = "block";
        if (senderFieldContainer) senderFieldContainer.style.display = "block";
        if (senderLabel) senderLabel.textContent = "Sender Email Address";
        if (senderInput) senderInput.placeholder = "e.g. security-alert@protection-service.net";
        if (smsSegmentsContainer) smsSegmentsContainer.style.display = "none";
      } else if (channel === "whatsapp") {
        if (emailSubjectContainer) emailSubjectContainer.style.display = "none";
        if (senderFieldContainer) senderFieldContainer.style.display = "block";
        if (senderLabel) senderLabel.textContent = "Sender Contact / Phone Number";
        if (senderInput) senderInput.placeholder = "e.g. +44 7911 123456 or Unknown International Number";
        if (smsSegmentsContainer) smsSegmentsContainer.style.display = "none";
      } else {
        // SMS
        if (emailSubjectContainer) emailSubjectContainer.style.display = "none";
        if (senderFieldContainer) senderFieldContainer.style.display = "block";
        if (senderLabel) senderLabel.textContent = "Sender ID or Number";
        if (senderInput) senderInput.placeholder = "e.g. +1 (800) 555-0199 or AX-HDFCBK";
        if (smsSegmentsContainer) smsSegmentsContainer.style.display = "inline-flex";
      }

      // Update placeholder
      if (textarea && PLACEHOLDERS[channel]) {
        textarea.placeholder = PLACEHOLDERS[channel];
      }

      updateCounters();
    });
  });

  // 2. Real-time Character & Word Counter
  function updateCounters() {
    if (!textarea) return;

    const text = textarea.value;
    const charCount = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;

    if (charCountEl) charCountEl.textContent = charCount.toLocaleString();
    if (wordCountEl) wordCountEl.textContent = words.toLocaleString();

    // SMS Segments calculation (160 GSM chars per segment)
    if (smsSegmentsEl) {
      const segments = charCount === 0 ? 0 : (charCount <= 160 ? 1 : Math.ceil(charCount / 153));
      smsSegmentsEl.textContent = segments;
    }

    // Progress Bar percentage
    if (progressFill) {
      const pct = Math.min(100, (charCount / MAX_CHARS) * 100);
      progressFill.style.width = `${pct}%`;

      progressFill.classList.remove("limit-warn", "limit-danger");
      if (pct > 80) {
        progressFill.classList.add("limit-danger");
      } else if (pct > 50) {
        progressFill.classList.add("limit-warn");
      }
    }
  }

  if (textarea) {
    textarea.addEventListener("input", updateCounters);
    // Initial run
    updateCounters();
  }

  // 3. Clear Message Handler
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (textarea) {
        textarea.value = "";
        textarea.focus();
      }
      if (senderInput) senderInput.value = "";
      if (subjectInput) subjectInput.value = "";

      const existingResult = document.getElementById("scan_result_section");
      if (existingResult) {
        existingResult.style.opacity = "0.4";
      }

      updateCounters();
    });
  }

  // 4. Quick Load Sample Scam Handler
  if (sampleBtn) {
    sampleBtn.addEventListener("click", async () => {
      const activeChannel = messageTypeInput ? messageTypeInput.value : "sms";

      try {
        const response = await fetch(`/scanner/sample/${activeChannel}`);
        const data = await response.json();

        if (data.success && data.sample) {
          const s = data.sample;
          if (textarea) textarea.value = s.content || "";
          if (senderInput && s.sender) senderInput.value = s.sender;
          if (subjectInput && s.subject) subjectInput.value = s.subject;

          updateCounters();
          if (textarea) textarea.focus();
        }
      } catch (err) {
        console.error("Failed to load sample:", err);
      }
    });
  }
});
