/** Перемикання вкладок із підтримкою клавіатури. */
export function createTabs({ root, onChange }) {
  const buttons = [...root.querySelectorAll("[data-tab]")];

  function activate(name, focus = false) {
    buttons.forEach((button) => {
      const active = button.dataset.tab === name;
      button.classList.toggle("tab--active", active);
      button.setAttribute("aria-selected", String(active));
      button.tabIndex = active ? 0 : -1;
      if (active && focus) button.focus();
    });
    onChange?.(name);
  }

  buttons.forEach((button, index) => {
    button.addEventListener("click", () => activate(button.dataset.tab));
    button.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
      event.preventDefault();
      const step = event.key === "ArrowRight" ? 1 : -1;
      const next = buttons[(index + step + buttons.length) % buttons.length];
      activate(next.dataset.tab, true);
    });
  });

  return activate;
}
