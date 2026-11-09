import { fromHTML } from "../core/markup.js";

const TEMPLATE = `
<dialog class="key-dialog" data-dialog>
  <form class="key-dialog__form" data-form novalidate>
    <h2 class="card__title">Експорт приватного ключа</h2>
    <p class="card__lead">Ключ буде зашифровано парольною фразою у форматі PKCS#8.</p>
    <label class="field">
      <span class="field__label">Парольна фраза</span>
      <input class="field__input" type="password" data-passphrase
             minlength="8" autocomplete="new-password" required>
    </label>
    <p class="field__error" data-error role="alert"></p>
    <div class="key-dialog__actions">
      <button class="btn btn--line" type="button" data-cancel>Скасувати</button>
      <button class="btn btn--solid" type="submit" data-submit>Завантажити</button>
    </div>
  </form>
</dialog>
`;

export function createExportDialog() {
  const dialog = fromHTML(TEMPLATE);
  const input = dialog.querySelector("[data-passphrase]");
  const error = dialog.querySelector("[data-error]");
  const submit = dialog.querySelector("[data-submit]");

  let resolver = null;
  let handler = null;

  function close(result) {
    if (!resolver) return;
    dialog.close();
    const resolve = resolver;
    resolver = null;
    resolve(result);
  }

  dialog.querySelector("[data-form]").addEventListener("submit", async (event) => {
    event.preventDefault();
    error.textContent = "";

    if (input.value.length < 8) {
      error.textContent = "Парольна фраза має містити щонайменше 8 символів.";
      return;
    }

    submit.disabled = true;
    try {
      await handler(input.value);
      close(true);
    } catch (failure) {
      error.textContent = failure.message || "Не вдалося експортувати ключ.";
    } finally {
      submit.disabled = false;
    }
  });

  dialog.querySelector("[data-cancel]").addEventListener("click", () => close(false));
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    close(false);
  });

  function open(onExport) {
    handler = onExport;
    input.value = "";
    error.textContent = "";
    dialog.showModal();
    input.focus();
    return new Promise((resolve) => {
      resolver = resolve;
    });
  }

  return { element: dialog, open };
}
