/** Робота з формою: збір значень, позначки помилок, стан зайнятості. */

export function values(form) {
  return Object.fromEntries(new FormData(form).entries());
}

export function resetMarks(form) {
  form.querySelectorAll("[data-error-for]").forEach((node) => {
    node.textContent = "";
  });
  form.querySelectorAll(".field__input").forEach((input) => {
    input.classList.remove("is-invalid");
  });
  const notice = form.querySelector("[data-form-error]");
  if (notice) {
    notice.hidden = true;
    notice.textContent = "";
  }
}

export function markFields(form, fields = {}) {
  Object.entries(fields).forEach(([name, messages]) => {
    const node = form.querySelector(`[data-error-for="${name}"]`);
    if (!node) return;
    node.textContent = Array.isArray(messages) ? messages.join(" · ") : String(messages);
    node.closest(".field")?.querySelector(".field__input")?.classList.add("is-invalid");
  });
  form.querySelector(".field__input.is-invalid")?.focus();
}

export function showNotice(form, message) {
  const notice = form.querySelector("[data-form-error]");
  if (!notice) return;
  notice.textContent = message;
  notice.hidden = false;
}

export function setBusy(form, busy, label = "Хвилинку…") {
  const button = form.querySelector('button[type="submit"]');
  if (!button) return;
  const caption = button.querySelector("[data-label]");
  if (caption && !button.dataset.idle) button.dataset.idle = caption.textContent;
  if (caption) caption.textContent = busy ? label : button.dataset.idle || "";
  button.disabled = busy;
}

export function clearOnInput(form) {
  form.querySelectorAll(".field__input").forEach((input) => {
    input.addEventListener("input", () => {
      input.classList.remove("is-invalid");
      const node = form.querySelector(`[data-error-for="${input.name}"]`);
      if (node) node.textContent = "";
      const notice = form.querySelector("[data-form-error]");
      if (notice) notice.hidden = true;
    });
  });
}
