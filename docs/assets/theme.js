"use strict";

(() => {
  const key = "hardcorefamilia-theme";
  const themes = ["system", "light", "dark"];
  const root = document.documentElement;

  function apply(theme) {
    if (theme === "system") delete root.dataset.theme;
    else root.dataset.theme = theme;
  }

  let theme = "system";
  try {
    const saved = localStorage.getItem(key);
    if (themes.includes(saved)) theme = saved;
  } catch {
    // The system preference still works if browser storage is unavailable.
  }
  apply(theme);

  document.addEventListener("DOMContentLoaded", () => {
    const picker = document.querySelector("#theme");
    picker.value = theme;
    picker.parentElement.hidden = false;
    picker.addEventListener("change", () => {
      apply(picker.value);
      try {
        localStorage.setItem(key, picker.value);
      } catch {
        // The selected theme still applies to the current page.
      }
    });
  });
})();
