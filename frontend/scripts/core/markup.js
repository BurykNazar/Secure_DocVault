const SPRITE = "/static/assets/icons.svg?v=6";

/** Перетворює рядок розмітки на готовий елемент. */
export function fromHTML(source) {
  const holder = document.createElement("template");
  holder.innerHTML = source.trim();
  return holder.content.firstElementChild;
}

/** Посилання на власну іконку зі спрайта. */
export function icon(name, modifier = "") {
  return `<svg class="icon ${modifier}" aria-hidden="true"><use href="${SPRITE}#${name}"></use></svg>`;
}
