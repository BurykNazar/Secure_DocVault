/** Короткі сповіщення внизу ліворуч. */

export function toast(message, tone = "ok") {
  const stack = document.getElementById("toasts");
  if (!stack) return;

  const node = document.createElement("div");
  node.className = tone === "bad" ? "toast toast--bad" : "toast";
  node.textContent = message;
  stack.append(node);

  window.setTimeout(() => node.classList.add("toast--out"), 3200);
  window.setTimeout(() => node.remove(), 3500);
}
