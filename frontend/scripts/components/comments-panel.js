import { call } from "../core/http.js";
import { fromHTML } from "../core/markup.js";
import { toast } from "../ui/toast.js";
import { createCommentForm } from "./comments-form.js";
import { createCommentItem } from "./comment-item.js";

const TEMPLATE = `
<section class="card comments">
  <header class="card__head">
    <p class="card__kicker">Особистий простір</p>
    <h2 class="card__title">Мої коментарі</h2>
    <p class="card__lead">Тут видно лише ваші записи.</p>
  </header>
  <div data-form-host></div>
  <div class="comments__list" data-list></div>
</section>
`;

export function createCommentsPanel() {
  const panel = fromHTML(TEMPLATE);
  const list = panel.querySelector("[data-list]");
  const form = createCommentForm({ onSaved: () => load() });

  function render(items) {
    list.replaceChildren();
    if (!items.length) {
      const empty = document.createElement("p");
      empty.className = "comments__empty";
      empty.textContent = "Ще немає коментарів.";
      list.append(empty);
      return;
    }
    for (const item of items) {
      list.append(createCommentItem(item, { onEdit: form.startEdit, onDelete: remove }));
    }
  }

  async function load() {
    try {
      render((await call("/api/v1/comments")).comments);
    } catch (error) {
      toast(error.message || "Не вдалося завантажити коментарі.", "bad");
    }
  }

  async function remove(item) {
    if (!window.confirm("Видалити цей коментар?")) return;
    try {
      await call(`/api/v1/comments/${item.id}`, { method: "DELETE" });
      if (form.currentId() === item.id) form.reset();
      toast("Коментар видалено.");
      load();
    } catch (error) {
      toast(error.message || "Не вдалося видалити.", "bad");
    }
  }

  panel.querySelector("[data-form-host]").append(form.element);
  load();

  return panel;
}
