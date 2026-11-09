/** Форматування часу коментаря. */

export function timestamp(value) {
  if (!value) return "";
  const iso = value.includes("T") ? value : `${value.replace(" ", "T")}Z`;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("uk-UA", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
