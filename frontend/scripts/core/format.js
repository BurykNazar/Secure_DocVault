/** Людське відображення даних облікового запису. */

export function initials(name = "") {
  const parts = name
    .replace(/[_.\-]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  const letters = parts.slice(0, 2).map((part) => part[0]);
  return (letters.join("") || "?").toUpperCase();
}

export function longDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("uk-UA", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function accessName(role) {
  return role === "admin" ? "Адміністратор" : "Користувач";
}

export function shortHash(value) {
  if (!value) return "—";
  return value.length <= 24 ? value : `${value.slice(0, 12)}…${value.slice(-8)}`;
}
