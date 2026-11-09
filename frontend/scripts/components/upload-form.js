import { RequestFailed } from "../core/errors.js";
import { upload } from "../core/http.js";
import { resetMarks, setBusy, showNotice } from "../core/dom.js";
import { fromHTML, icon } from "../core/markup.js";
import { toast } from "../ui/toast.js";

const TEMPLATE = `
<form class="form" data-form novalidate>
  <label class="dropzone" data-drop>
    <input class="visually-hidden" type="file" name="file" data-file>
    <span class="dropzone__icon">${icon("upload")}</span>
    <span class="dropzone__title">Перетягніть файл сюди</span>
    <span class="dropzone__hint">або натисніть, щоб вибрати · до 10 МБ</span>
    <span class="dropzone__name" data-name hidden></span>
  </label>
  <p class="form__notice" data-form-error role="alert" hidden></p>
  <div class="comments__actions">
    <button class="btn btn--solid" type="submit"><span data-label>Завантажити</span></button>
  </div>
</form>
`;

export function createUploadForm({ onUploaded }) {
  const form = fromHTML(TEMPLATE);
  const drop = form.querySelector("[data-drop]");
  const input = form.querySelector("[data-file]");
  const name = form.querySelector("[data-name]");

  function showName() {
    const file = input.files && input.files[0];
    name.textContent = file ? file.name : "";
    name.hidden = !file;
  }

  input.addEventListener("change", showName);

  ["dragenter", "dragover"].forEach((type) => {
    drop.addEventListener(type, (event) => {
      event.preventDefault();
      drop.classList.add("is-dragging");
    });
  });

  ["dragleave", "drop"].forEach((type) => {
    drop.addEventListener(type, (event) => {
      event.preventDefault();
      drop.classList.remove("is-dragging");
    });
  });

  drop.addEventListener("drop", (event) => {
    if (!event.dataTransfer.files.length) return;
    const transfer = new DataTransfer();
    for (const file of event.dataTransfer.files) transfer.items.add(file);
    input.files = transfer.files;
    showName();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetMarks(form);
    if (!input.files || !input.files[0]) {
      showNotice(form, "Оберіть файл.");
      return;
    }

    const data = new FormData();
    data.append("file", input.files[0]);
    setBusy(form, true, "Шифруємо…");

    try {
      await upload("/api/v1/documents/upload", data);
      form.reset();
      showName();
      toast("Файл зашифровано та збережено.");
      onUploaded();
    } catch (error) {
      if (error instanceof RequestFailed) {
        showNotice(form, error.message);
        toast(error.message, "bad");
      } else {
        showNotice(form, "Не вдалося завантажити файл.");
      }
    } finally {
      setBusy(form, false);
    }
  });

  return { element: form };
}
