import { call } from "../core/http.js";
import { fetchFile, saveBlob } from "../core/download.js";
import { longDate } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";
import { toast } from "../ui/toast.js";
import { confirmDelete } from "./confirm-dialog.js";

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
    <button class="link" type="button" data-download>Скачати</button>
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
      const signature = document.signature || {};
      const signed =
        signature.status === "signed" || signature.status === "verified";
      const meta = node.querySelector(".doc__meta");

      node.querySelector(".doc__name").textContent = document.original_filename;
      meta.textContent =
        `${sizeLabel(document.size_bytes)} · ${longDate(document.created_at)}` +
        ` · ${signed ? "Підписано" : "Без підпису"}`;
      meta.classList.toggle("doc__meta--signed", signed);
      meta.title = signed
        ? `Підписано: ${signature.signer || "—"}`
        : "Документ без ЕЦП";
      node
        .querySelector("[data-download]")
        .addEventListener("click", () => download(document));
      node
        .querySelector("[data-delete]")
        .addEventListener("click", () => remove(document));
      root.append(node);
    }
  }

  async function download(document) {
    try {
      const result = await fetchFile(
        `/api/v1/documents/${document.id}/download`
      );
      saveBlob(result.blob, document.original_filename);
      const status = result.headers.get("X-Signature-Status");
      toast(
        status === "Signed & Verified"
          ? "Файл розшифровано. Підпис перевірено."
          : "Файл розшифровано та завантажено."
      );
    } catch (error) {
      toast(error.message || "Не вдалося скачати документ.", "bad");
    }
  }

  async function remove(document) {
    const confirmed = await confirmDelete({
      title: "Видалити документ?",
      message: `«${document.original_filename}» буде видалено разом із підписом.`,
    });
    if (!confirmed) return;
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
