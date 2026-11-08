import { fromHTML } from "../core/markup.js";
import { createTabs } from "../ui/tabs.js";
import { createSignInForm } from "./sign-in-form.js";
import { createSignUpForm } from "./sign-up-form.js";

const SHELL = `
<div class="stack">
  <section class="card">
    <header class="card__head">
      <p class="card__kicker" data-kicker></p>
      <h2 class="card__title" data-title></h2>
      <p class="card__lead" data-lead></p>
    </header>
    <div class="tabs" role="tablist" aria-label="Вхід або реєстрація">
      <button class="tab tab--active" type="button" role="tab" aria-selected="true" data-tab="signin">Вхід</button>
      <button class="tab" type="button" role="tab" aria-selected="false" data-tab="signup" tabindex="-1">Реєстрація</button>
    </div>
    <div data-panel="signin"></div>
    <div data-panel="signup" hidden></div>
  </section>
  <p class="card__legal">© 2026 Secure DocVault. Усі права захищені.</p>
</div>
`;

const COPY = {
  signin: {
    kicker: "Обліковий запис",
    title: "З поверненням",
    lead: "Увійдіть, щоб відкрити сховище.",
  },
  signup: {
    kicker: "Новий обліковий запис",
    title: "Створити акаунт",
    lead: "Заповніть форму — і сховище буде готове.",
  },
};

export function createGate({ onSignedIn }) {
  const shell = fromHTML(SHELL);
  const signinPanel = shell.querySelector('[data-panel="signin"]');
  const signupPanel = shell.querySelector('[data-panel="signup"]');
  const kicker = shell.querySelector("[data-kicker]");
  const title = shell.querySelector("[data-title]");
  const lead = shell.querySelector("[data-lead]");

  const signIn = createSignInForm({ onSignedIn });
  signinPanel.append(signIn);

  const signUp = createSignUpForm({
    onCreated(account) {
      activate("signin", true);
      signIn.suggest(account.username);
    },
  });
  signupPanel.append(signUp);

  const activate = createTabs({
    root: shell.querySelector(".tabs"),
    onChange(name) {
      kicker.textContent = COPY[name].kicker;
      title.textContent = COPY[name].title;
      lead.textContent = COPY[name].lead;
      signinPanel.hidden = name !== "signin";
      signupPanel.hidden = name !== "signup";
    },
  });

  activate("signin");
  return shell;
}
