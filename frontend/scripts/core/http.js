import { RequestFailed } from "./errors.js";

/**
 * Єдина точка звернення до сервера.
 * Сервер відповідає структурою { ok, error: { code, message, fields } },
 * тому тут вона перетворюється на виняток RequestFailed.
 */
export async function call(path, { method = "GET", data } = {}) {
  let response;

  try {
    response = await fetch(path, {
      method,
      cache: "no-store",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        ...(data === undefined ? {} : { "Content-Type": "application/json" }),
      },
      body: data === undefined ? undefined : JSON.stringify(data),
    });
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
