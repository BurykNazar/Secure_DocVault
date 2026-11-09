import { call } from "../core/http.js";
import { fromHTML } from "../core/markup.js";
import { toast } from "../ui/toast.js";
import { createCommentsPanel } from "./comments-panel.js";
import { createDocumentList } from "./document-list.js";
import { createSignaturePanel } from "./signature-panel.js";
import { createUploadForm } from "./upload-form.js";

const TEMPLATE = `
<div class="documents">
  <div data-signature-host></div>
  <section class="card">
    <header class="card__head">
      <p class="card__kicker">Сховище</p>
      <h2 class="card__title">Мої документи</h2>
      <p class="card__lead">Файли зберігаються лише у зашифрованому вигляді.</p>
    </header>
    <div data-upload-host></div>
    <div data-list-host></div>
  </section>
  <div data-comments-host></div>
</div>
`;

export function createDocumentsPanel() {
  const panel = fromHTML(TEMPLATE);
  const comments = createCommentsPanel();
  const signature = createSignaturePanel();
  const list = createDocumentList({ onChanged: () => load() });
  const upload = createUploadForm({
    onUploaded: () => {
      load();
      signature.load();
    },
  });

  panel.querySelector("[data-signature-host]").append(signature.element);
  panel.querySelector("[data-upload-host]").append(upload.element);
  panel.querySelector("[data-list-host]").append(list.element);
  panel.querySelector("[data-comments-host]").append(comments.element);

  async function load() {
    try {
      const data = await call("/api/v1/documents");
      list.render(data.documents);
      comments.setDocuments(data.documents);
    } catch (error) {
      toast(error.message || "Не вдалося завантажити документи.", "bad");
    }
  }

  load();
  return panel;
}
