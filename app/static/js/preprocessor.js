/**
 * SMART SCAM MESSAGE DETECTION SYSTEM
 * Module 3: Message Preprocessor Studio Client Script
 */

document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("preprocessor_input_text");
  const clearBtn = document.getElementById("btn_clear_preprocessor");
  const samplePills = document.querySelectorAll(".sample-pill-btn");

  // Sample pill quick-fill
  samplePills.forEach(pill => {
    pill.addEventListener("click", async () => {
      const key = pill.getAttribute("data-sample-key");
      try {
        const response = await fetch(`/preprocessor/sample/${key}`);
        const data = await response.json();
        if (data.success && data.sample && textarea) {
          textarea.value = data.sample.text || "";
          textarea.focus();
        }
      } catch (err) {
        console.error("Error loading sample:", err);
      }
    });
  });

  // Clear button
  if (clearBtn && textarea) {
    clearBtn.addEventListener("click", () => {
      textarea.value = "";
      textarea.focus();
      const resultCard = document.getElementById("preprocessor_results_wrapper");
      if (resultCard) {
        resultCard.style.opacity = "0.3";
      }
    });
  }

  // Token filter toggles
  const filterBtns = document.querySelectorAll(".token-filter-btn");
  if (filterBtns.length > 0) {
    filterBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetClass = btn.getAttribute("data-filter");
        filterBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const allChips = document.querySelectorAll(".token-chip");
        allChips.forEach(chip => {
          if (targetClass === "all") {
            chip.style.display = "inline-flex";
          } else if (chip.classList.contains(targetClass)) {
            chip.style.display = "inline-flex";
          } else {
            chip.style.display = "none";
          }
        });
      });
    });
  }
});
