import { call } from "../core/http.js";
import { longDate } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";
import { toast } from "../ui/toast.js";

const EMPTY = `<p class="documents__empty">Ще немає документів.</p>`;

const ITEM = `
<article class="doc">
  <div class="doc__main">
    <span class="doc__icon">${icon("shield")}</span>
    <div>
      <h3 class="doc__name"></h3>
      <p class="doc__meta"></p>
    </div>
  </div>
  <div class="doc__actions">
    <a class="link" data-download href="#" download>Скачати</a>
    <button class="link link--danger" type="button" data-delete>Видалити</button>
  </div>
</article>
`;

function sizeLabel(bytes) {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
}

export function createDocumentList({ onChanged }) {
  const root = fromHTML(`<div class="documents__list"></div>`);

  function render(documents) {
    root.replaceChildren();
    if (!documents.length) {
      root.innerHTML = EMPTY;
      return;
    }
    for (const document of documents) {
      const node = fromHTML(ITEM);
      node.querySelector(".doc__name").textContent = document.original_filename;
      node.querySelector(".doc__meta").textContent =
        `${sizeLabel(document.size_bytes)} · ${longDate(document.created_at)}`;
      node.querySelector("[data-download]").href =
        `/api/v1/documents/${document.id}/download`;
      node.querySelector("[data-delete]").addEventListener("click", () =>
        remove(document)
      );
      root.append(node);
    }
  }

  async function remove(document) {
    if (!window.confirm(`Видалити «${document.original_filename}»?`)) return;
    try {
      await call(`/api/v1/documents/${document.id}`, { method: "DELETE" });
      toast("Документ видалено.");
      onChanged();
    } catch (error) {
      toast(error.message || "Не вдалося видалити.", "bad");
    }
  }

  return { element: root, render };
}
