/** Помилка запиту з полями, які треба підсвітити у формі. */
export class RequestFailed extends Error {
  constructor(status, payload) {
    super(payload?.error?.message || "Не вдалося виконати запит");
    this.name = "RequestFailed";
    this.status = status;
    this.code = payload?.error?.code || "unknown";
    this.fields = payload?.error?.fields || {};
  }
}
