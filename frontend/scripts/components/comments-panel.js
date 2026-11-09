import { call } from "../core/http.js";
import { fromHTML } from "../core/markup.js";
import { toast } from "../ui/toast.js";
import { createCommentForm } from "./comment-form.js";
import { createCommentItem } from "./comment-item.js";

const TEMPLATE = `
<section class="card comments">
  <header class="card__head">
    <p class="card__kicker">Обговорення</p>
    <h2 class="card__title">Коментарі до документа</h2>
  </header>
  <div class="field comments__doc">
    <label class="field__label" for="comment-doc">Документ</label>
    <select class="field__input" id="comment-doc" data-doc></select>
  </div>
  <div data-form-host></div>
  <div class="comments__list" data-list></div>
</section>
`;

export function createCommentsPanel() {
  const panel = fromHTML(TEMPLATE);
  const select = panel.querySelector("[data-doc]");
  const list = panel.querySelector("[data-list]");
  const formHost = panel.querySelector("[data-form-host]");
  let documentId = null;

  const form = createCommentForm({
    getDocumentId: () => documentId,
    onSaved: () => load(),
  });
  formHost.append(form.element);
  function showEmpty(text) {
    const empty = document.createElement("p");
    empty.className = "comments__empty";
    empty.textContent = text;
    list.replaceChildren(empty);
  }
  function render(items) {
    if (!documentId) return showEmpty("Спочатку завантажте документ.");
    if (!items.length) return showEmpty("Ще немає коментарів.");
    list.replaceChildren();
    for (const item of items) {
      list.append(createCommentItem(item, { onEdit: form.startEdit, onDelete: remove }));
    }
  }
  async function load() {
    if (!documentId) {
      formHost.hidden = true;
      return showEmpty("Спочатку завантажте документ.");
    }
    formHost.hidden = false;
    try {
      const data = await call(`/api/v1/documents/${documentId}/comments`);
      render(data.comments);
    } catch (error) {
      toast(error.message || "Не вдалося завантажити коментарі.", "bad");
    }
  }
  function setDocuments(documents) {
    const previous = documentId;
    select.replaceChildren();
    documentId = null;
    for (const item of documents) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.original_filename;
      select.append(option);
    }
    if (documents.length) {
      const keep = documents.some((doc) => String(doc.id) === String(previous));
      documentId = keep ? previous : documents[0].id;
      select.value = documentId;
    }
    form.reset();
    load();
  }
  async function remove(item) {
    if (!window.confirm("Видалити цей коментар?")) return;
    try {
      await call(`/api/v1/documents/${documentId}/comments/${item.id}`, {
        method: "DELETE",
      });
      if (form.currentId() === item.id) form.reset();
      toast("Коментар видалено.");
      load();
    } catch (error) {
      toast(error.message || "Не вдалося видалити.", "bad");
    }
  }
  select.addEventListener("change", () => {
    documentId = select.value || null;
    form.reset();
    load();
  });

  return { element: panel, setDocuments };
}
