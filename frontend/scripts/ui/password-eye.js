/** Показ і приховування введеного пароля. */
export function bindPasswordEyes(root) {
  root.querySelectorAll("[data-reveal]").forEach((button) => {
    const input = button.closest(".field__wrap")?.querySelector("input");
    if (!input) return;

    button.addEventListener("click", () => {
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.setAttribute("aria-pressed", String(reveal));
      button.setAttribute("aria-label", reveal ? "Сховати пароль" : "Показати пароль");
      input.focus({ preventScroll: true });
    });
  });
}
