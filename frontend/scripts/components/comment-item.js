import { fromHTML } from "../core/markup.js";
import { timestamp } from "../ui/timestamp.js";

const TEMPLATE = `
<article class="note">
  <header class="note__head">
    <h3 class="note__title"></h3>
    <time class="note__time"></time>
  </header>
  <p class="note__text"></p>
  <div class="note__actions">
    <button class="link" type="button" data-edit>Змінити</button>
    <button class="link link--danger" type="button" data-delete>Видалити</button>
  </div>
</article>
`;

export function createCommentItem(comment, { onEdit, onDelete }) {
  const node = fromHTML(TEMPLATE);

  node.querySelector(".note__title").textContent = comment.title;
  node.querySelector(".note__text").textContent = comment.comment;
  node.querySelector(".note__time").textContent = timestamp(
    comment.updated_at || comment.created_at
  );
  node.querySelector("[data-edit]").addEventListener("click", () => onEdit(comment));
  node.querySelector("[data-delete]").addEventListener("click", () => onDelete(comment));

  return node;
}
