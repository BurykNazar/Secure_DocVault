import { RequestFailed } from "./errors.js";

async function perform(path, options) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new RequestFailed(0, {
      error: {
        code: "offline",
        message: "Сервіс недоступний. Спробуйте трохи пізніше.",
      },
    });
  }
  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new RequestFailed(response.status, payload);
  return payload;
}

export function call(path, { method = "GET", data } = {}) {
  return perform(path, {
    method,
    cache: "no-store",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      ...(data === undefined ? {} : { "Content-Type": "application/json" }),
    },
    body: data === undefined ? undefined : JSON.stringify(data),
  });
}

export function upload(path, formData) {
  return perform(path, {
    method: "POST",
    cache: "no-store",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
    body: formData,
  });
}
