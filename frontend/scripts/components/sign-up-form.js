import { RequestFailed } from "../core/errors.js";
import { call } from "../core/http.js";
import { clearOnInput, markFields, resetMarks, setBusy, showNotice, values } from "../core/dom.js";
import { fromHTML, icon } from "../core/markup.js";
import { bindPasswordEyes } from "../ui/password-eye.js";
import { toast } from "../ui/toast.js";

const TEMPLATE = `
<form class="form" novalidate>
  <div class="field">
    <label class="field__label" for="signup-username">Ім'я користувача</label>
    <input class="field__input" id="signup-username" name="username" type="text" autocomplete="username" spellcheck="false" maxlength="30" placeholder="Латиниця, цифри, «_»">
    <p class="field__error" data-error-for="username"></p>
  </div>
  <div class="field">
    <label class="field__label" for="signup-email">Електронна пошта</label>
    <input class="field__input" id="signup-email" name="email" type="email" autocomplete="email" spellcheck="false" maxlength="254" placeholder="name@company.com">
    <p class="field__error" data-error-for="email"></p>
  </div>
  <div class="field">
    <label class="field__label" for="signup-password">Пароль</label>
    <div class="field__wrap">
      <input class="field__input" id="signup-password" name="password" type="password" autocomplete="new-password" maxlength="128" placeholder="Придумайте пароль">
      <button class="field__reveal" type="button" data-reveal aria-label="Показати пароль" aria-pressed="false">${icon("eye", "icon--show")}${icon("eye-off", "icon--hide")}</button>
    </div>
    <ul class="rules"><li>8+ символів</li><li>велика й мала літери</li><li>цифра</li><li>спецсимвол</li></ul>
    <p class="field__error" data-error-for="password"></p>
  </div>
  <p class="form__notice" data-form-error role="alert" hidden></p>
  <button class="btn btn--solid" type="submit"><span data-label>Створити акаунт</span>${icon("check")}</button>
</form>
`;

export function createSignUpForm({ onCreated }) {
  const form = fromHTML(TEMPLATE);
  bindPasswordEyes(form);
  clearOnInput(form);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetMarks(form);
    setBusy(form, true, "Створюємо…");

    try {
      const answer = await call("/api/v1/accounts/register", {
        method: "POST",
        data: values(form),
      });
      form.reset();
      toast("Акаунт створено. Тепер увійдіть.");
      onCreated(answer.account);
    } catch (error) {
      if (error instanceof RequestFailed) {
        markFields(form, error.fields);
        if (!Object.keys(error.fields).length) showNotice(form, error.message);
        toast(error.message, "bad");
      } else {
        showNotice(form, "Сталася помилка. Спробуйте ще раз.");
      }
    } finally {
      setBusy(form, false);
    }
  });

  return form;
}
