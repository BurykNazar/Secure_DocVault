import { accessName, initials, longDate } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";

const TEMPLATE = `
<section class="card">
  <div class="who">
    <span class="who__avatar" data-initials aria-hidden="true"></span>
    <div>
      <p class="card__kicker">Ваш обліковий запис</p>
      <h2 class="who__name" data-name></h2>
    </div>
  </div>
  <dl class="facts">
    <div><dt>${icon("mail")} Пошта</dt><dd data-email></dd></div>
    <div><dt>${icon("user")} Доступ</dt><dd data-access></dd></div>
    <div><dt>${icon("clock")} Створено</dt><dd data-created></dd></div>
  </dl>
  <p class="card__note">${icon("shield")} Ви в захищеному просторі Secure DocVault.</p>
  <div class="account__actions">
    <button class="btn btn--line" type="button" data-leave>Вийти ${icon("logout")}</button>
  </div>
</section>
`;

export function createAccountView({ account, onLeave }) {
  const view = fromHTML(TEMPLATE);

  view.querySelector("[data-initials]").textContent = initials(account.username);
  view.querySelector("[data-name]").textContent = account.username;
  view.querySelector("[data-email]").textContent = account.email;
  view.querySelector("[data-access]").textContent = accessName(account.role);
  view.querySelector("[data-created]").textContent = longDate(account.created_at);
  view.querySelector("[data-leave]").addEventListener("click", onLeave);

  return view;
}
