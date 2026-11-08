import { RequestFailed } from "../core/errors.js";
import { call } from "../core/http.js";
import { clearOnInput, markFields, resetMarks, setBusy, showNotice, values } from "../core/dom.js";
import { fromHTML, icon } from "../core/markup.js";
import { bindPasswordEyes } from "../ui/password-eye.js";
import { toast } from "../ui/toast.js";

const TEMPLATE = `
<form class="form" novalidate>
  <div class="field">
    <label class="field__label" for="signin-username">Ім'я користувача</label>
    <input class="field__input" id="signin-username" name="username" type="text" autocomplete="username" spellcheck="false" maxlength="255" placeholder="Ваш логін">
    <p class="field__error" data-error-for="username"></p>
  </div>
  <div class="field">
    <label class="field__label" for="signin-password">Пароль</label>
    <div class="field__wrap">
      <input class="field__input" id="signin-password" name="password" type="password" autocomplete="current-password" maxlength="128" placeholder="Ваш пароль">
      <button class="field__reveal" type="button" data-reveal aria-label="Показати пароль" aria-pressed="false">${icon("eye", "icon--show")}${icon("eye-off", "icon--hide")}</button>
    </div>
    <p class="field__error" data-error-for="password"></p>
  </div>
  <p class="form__notice" data-form-error role="alert" hidden></p>
  <button class="btn btn--solid" type="submit"><span data-label>Увійти</span>${icon("arrow")}</button>
</form>
`;

export function createSignInForm({ onSignedIn }) {
  const form = fromHTML(TEMPLATE);
  bindPasswordEyes(form);
  clearOnInput(form);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetMarks(form);
    setBusy(form, true, "Перевіряємо…");

    try {
      const answer = await call("/api/v1/accounts/login", {
        method: "POST",
        data: values(form),
      });
      form.reset();
      onSignedIn(answer.account);
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

  form.suggest = (username) => {
    form.elements.username.value = username;
    form.elements.password.value = "";
    form.elements.password.focus();
  };

  return form;
}
