import { initials } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";
import { createTabs } from "../ui/tabs.js";
import { createDocumentsPanel } from "./documents-panel.js";
import { createProfilePanel } from "./profile-panel.js";

const TEMPLATE = `
<section class="workspace">
  <header class="workspace__bar">
    <div class="who">
      <span class="who__avatar" data-initials aria-hidden="true"></span>
      <div>
        <p class="card__kicker">Ваш обліковий запис</p>
        <strong class="who__name" data-name></strong>
      </div>
    </div>
    <button class="btn btn--line" type="button" data-leave>Вийти ${icon("logout")}</button>
  </header>
  <div class="tabs" role="tablist" aria-label="Розділи сховища">
    <button class="tab tab--active" type="button" role="tab" aria-selected="true" data-tab="profile">Профіль</button>
    <button class="tab" type="button" role="tab" aria-selected="false" data-tab="documents" tabindex="-1">Документи</button>
  </div>
  <div data-panel="profile"></div>
  <div data-panel="documents" hidden></div>
</section>
`;

export function createWorkspace({ account, onLeave }) {
  const root = fromHTML(TEMPLATE);
  root.querySelector("[data-initials]").textContent = initials(account.username);
  root.querySelector("[data-name]").textContent = account.username;
  root.querySelector("[data-leave]").addEventListener("click", onLeave);

  const profileHost = root.querySelector('[data-panel="profile"]');
  const documentsHost = root.querySelector('[data-panel="documents"]');
  profileHost.append(createProfilePanel(account));
  documentsHost.append(createDocumentsPanel());

  const activate = createTabs({
    root: root.querySelector(".tabs"),
    onChange(name) {
      profileHost.hidden = name !== "profile";
      documentsHost.hidden = name !== "documents";
    },
  });

  activate("profile");
  return root;
}
