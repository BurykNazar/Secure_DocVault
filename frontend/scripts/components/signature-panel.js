import { call } from "../core/http.js";
import { fetchFile, saveBlob } from "../core/download.js";
import { longDate, shortHash } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";
import { toast } from "../ui/toast.js";
import { createExportDialog } from "./export-key-dialog.js";

const TEMPLATE = `
<section class="card signature">
  <header class="card__head">
    <p class="card__kicker">ЕЦП</p>
    <h2 class="card__title">Цифровий підпис</h2>
    <p class="card__lead">Документи підписуються автоматично під час завантаження, а підпис перевіряється під час скачування.</p>
    <span class="signature__state" data-state>Ключ не створено</span>
  </header>
  <dl class="facts">
    <div><dt>${icon("user")} Відбиток</dt><dd class="signature__fingerprint" data-fingerprint>—</dd></div>
    <div><dt>${icon("clock")} Створено</dt><dd data-created>—</dd></div>
  </dl>
  <div class="signature__actions">
    <button class="btn btn--solid" type="button" data-generate>Створити ключі</button>
    <button class="btn btn--line" type="button" data-public hidden>Публічний ключ</button>
    <button class="btn btn--line" type="button" data-export hidden>Експорт приватного ключа</button>
  </div>
</section>
`;

export function createSignaturePanel() {
  const root = fromHTML(TEMPLATE);
  const dialog = createExportDialog(); root.append(dialog.element);

  const q = (selector) => root.querySelector(selector);
  const ui = {
    state: q("[data-state]"), fingerprint: q("[data-fingerprint]"),
    created: q("[data-created]"), generate: q("[data-generate]"),
    public: q("[data-public]"), export: q("[data-export]"),
  };

  function update(key) {
    const exists = Boolean(key);
    ui.state.textContent = exists ? "Ключ створено" : "Ключ не створено";
    ui.state.classList.toggle("signature__state--on", exists);
    ui.fingerprint.textContent = shortHash(key?.fingerprint);
    ui.fingerprint.title = exists ? key.fingerprint : "";
    ui.created.textContent = exists ? longDate(key.created_at) : "—";
    ui.generate.hidden = exists;
    ui.public.hidden = !exists;
    ui.export.hidden = !exists;
  }

  async function load() {
    try {
      update((await call("/api/v1/signing/keys")).key);
    } catch (failure) {
      if (failure.status !== 401) toast(failure.message, "bad");
    }
  }

  ui.generate.addEventListener("click", async () => {
    ui.generate.disabled = true;
    ui.generate.textContent = "Створюємо…";
    try {
      const data = await call("/api/v1/signing/keys", { method: "POST" });
      update(data.key);
      toast("Ключі ЕЦП створено.");
    } catch (failure) {
      toast(failure.message || "Не вдалося створити ключі.", "bad");
    } finally {
      ui.generate.disabled = false;
      ui.generate.textContent = "Створити ключі";
    }
  });

  ui.public.addEventListener("click", async () => {
    try {
      const { blob } = await fetchFile("/api/v1/signing/keys/public");
      saveBlob(blob, "docvault-public-key.pem");
      toast("Публічний ключ завантажено.");
    } catch (failure) {
      toast(failure.message || "Не вдалося завантажити ключ.", "bad");
    }
  });

  ui.export.addEventListener("click", () =>
    dialog.open(async (passphrase) => {
      const { blob } = await fetchFile("/api/v1/signing/keys/export", {
        method: "POST",
        data: { passphrase },
      });
      saveBlob(blob, "docvault-private-key.pem");
      toast("Приватний ключ завантажено. Збережіть його надійно.");
    })
  );

  load();
  return { element: root, load };
}
