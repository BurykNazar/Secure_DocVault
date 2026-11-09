import { RequestFailed } from "../core/errors.js";
import { call } from "../core/http.js";
import { clearOnInput, markFields, resetMarks, setBusy, showNotice, values } from "../core/dom.js";
import { fromHTML } from "../core/markup.js";
import { toast } from "../ui/toast.js";

const TEMPLATE = `
<form class="form" data-form novalidate>
  <div class="field">
    <label class="field__label" for="comment-title">Заголовок</label>
    <input class="field__input" id="comment-title" name="title" maxlength="200" placeholder="Наприклад, звіт за квартал">
    <p class="field__error" data-error-for="title"></p>
  </div>
  <div class="field">
    <label class="field__label" for="comment-text">Текст</label>
    <textarea class="field__input field__input--area" id="comment-text" name="comment" maxlength="4000" rows="3" placeholder="Ваш коментар"></textarea>
    <p class="field__error" data-error-for="comment"></p>
  </div>
  <p class="form__notice" data-form-error role="alert" hidden></p>
  <div class="comments__actions">
    <button class="btn btn--solid" type="submit"><span data-label>Додати</span></button>
    <button class="btn btn--line" type="button" data-cancel hidden>Скасувати</button>
  </div>
</form>
`;

export function createCommentForm({ onSaved }) {
  const form = fromHTML(TEMPLATE);
  const submitLabel = form.querySelector("[data-label]");
  const cancel = form.querySelector("[data-cancel]");
  let editingId = null;

  function reset() {
    form.reset();
    editingId = null;
    submitLabel.textContent = "Додати";
    cancel.hidden = true;
    resetMarks(form);
  }

  function startEdit(item) {
    editingId = item.id;
    form.elements.title.value = item.title;
    form.elements.comment.value = item.comment;
    submitLabel.textContent = "Зберегти";
    cancel.hidden = false;
    form.elements.title.focus();
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetMarks(form);
    setBusy(form, true, "Зберігаємо…");
    const data = values(form);
    try {
      if (editingId) {
        await call(`/api/v1/comments/${editingId}`, { method: "PUT", data });
      } else {
        await call("/api/v1/comments", { method: "POST", data });
      }
      toast(editingId ? "Коментар оновлено." : "Коментар додано.");
      reset();
      onSaved();
    } catch (error) {
      if (error instanceof RequestFailed) {
        markFields(form, error.fields);
        if (!Object.keys(error.fields).length) showNotice(form, error.message);
        toast(error.message, "bad");
      } else {
        showNotice(form, "Сталася помилка. Спробуйте ще раз.");
      }
    } finally {
      setBusy(form, false);
    }
  });

  cancel.addEventListener("click", reset);
  clearOnInput(form);

  return { element: form, reset, startEdit, currentId: () => editingId };
}
