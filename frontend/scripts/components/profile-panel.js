import { accessName, longDate } from "../core/format.js";
import { fromHTML, icon } from "../core/markup.js";

const TEMPLATE = `
<section class="card">
  <header class="card__head">
    <p class="card__kicker">Обліковий запис</p>
    <h2 class="card__title">Профіль</h2>
    <p class="card__lead">Дані, з якими ви увійшли у сховище.</p>
  </header>
  <dl class="facts">
    <div><dt>${icon("mail")} Пошта</dt><dd data-email></dd></div>
    <div><dt>${icon("user")} Доступ</dt><dd data-access></dd></div>
    <div><dt>${icon("clock")} Створено</dt><dd data-created></dd></div>
  </dl>
  <p class="card__note">${icon("shield")} Ви в захищеному просторі Secure DocVault.</p>
</section>
`;

export function createProfilePanel(account) {
  const card = fromHTML(TEMPLATE);

  card.querySelector("[data-email]").textContent = account.email;
  card.querySelector("[data-access]").textContent = accessName(account.role);
  card.querySelector("[data-created]").textContent = longDate(account.created_at);

  return card;
}
