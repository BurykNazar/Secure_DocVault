import { RequestFailed } from "./errors.js";

export function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export async function fetchFile(path, { method = "GET", data } = {}) {
  const options = { method, credentials: "same-origin", cache: "no-store" };
  if (data !== undefined) {
    options.headers = {
      Accept: "application/json",
      "Content-Type": "application/json",
    };
    options.body = JSON.stringify(data);
  }

  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new RequestFailed(0, {
      error: { code: "offline", message: "Сервіс недоступний." },
    });
  }

  if (!response.ok) {
    const type = response.headers.get("content-type") || "";
    const payload = type.includes("application/json")
      ? await response.json().catch(() => null)
      : null;
    throw new RequestFailed(response.status, payload);
  }

  return { blob: await response.blob(), headers: response.headers };
}
