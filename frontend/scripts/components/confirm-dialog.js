import { fromHTML, icon } from "../core/markup.js";

const TEMPLATE = `
<dialog class="confirm-dialog" data-dialog
        aria-labelledby="confirm-title" aria-describedby="confirm-message">
  <div class="confirm-dialog__body">
    <span class="confirm-dialog__icon">${icon("trash")}</span>
    <h2 class="confirm-dialog__title" id="confirm-title" data-title></h2>
    <p class="confirm-dialog__text" id="confirm-message" data-message></p>
    <p class="confirm-dialog__note">Файл і його підпис буде видалено назавжди. Відновити не вдасться.</p>
    <div class="confirm-dialog__actions">
      <button class="btn btn--line" type="button" data-cancel>Скасувати</button>
      <button class="btn btn--danger" type="button" data-confirm>Видалити</button>
    </div>
  </div>
</dialog>
`;

let dialog = null;
let pending = null;

function close(result) {
  if (!pending) return;
  dialog.close();
  const resolve = pending;
  pending = null;
  resolve(result);
}

function ensureDialog() {
  if (dialog) return dialog;
  dialog = fromHTML(TEMPLATE);
  document.body.append(dialog);
  dialog.querySelector("[data-cancel]").addEventListener("click", () => close(false));
  dialog.querySelector("[data-confirm]").addEventListener("click", () => close(true));
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    close(false);
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) close(false);
  });
  return dialog;
}

export function confirmDelete({ title, message, confirmLabel = "Видалити", cancelLabel = "Скасувати" }) {
  const ui = ensureDialog();
  if (pending) close(false);

  ui.querySelector("[data-title]").textContent = title;
  ui.querySelector("[data-message]").textContent = message;
  ui.querySelector("[data-confirm]").textContent = confirmLabel;
  ui.querySelector("[data-cancel]").textContent = cancelLabel;

  ui.showModal();
  ui.querySelector("[data-cancel]").focus();
  return new Promise((resolve) => {
    pending = resolve;
  });
}
