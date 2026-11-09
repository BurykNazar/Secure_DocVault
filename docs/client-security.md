# Захист клієнтської частини

## Заголовки відповіді

| Заголовок | Значення | Що блокує |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; …` | XSS, підключення сторонніх скриптів |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `X-Content-Type-Options` | `nosniff` | MIME-sniffing |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | downgrade на HTTP |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | витік URL у Referer |

Для `/api/docs` діє окрема політика: Scalar малює сторінку
інлайн-скриптами й підвантажує код із `cdn.jsdelivr.net`. Решта
застосунку працює без `unsafe-inline`.

## Cookie

Після входу сервер ставить `vault_access`:

```text
HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
```

* `HttpOnly` — `document.cookie` порожній, XSS не читає токен;
* `SameSite=Strict` — браузер не надсилає cookie в міжсайтових
  запитах, що закриває CSRF;
* `Secure` — cookie передається лише захищеним каналом. На
  `http://localhost` браузер вважає з'єднання довіреним, тому демо
  працює; для `127.0.0.1` без HTTPS прапорець можна вимкнути через
  `VAULT_COOKIE_SECURE=false`.

## CORS

Дозволені лише адреси з `VAULT_CORS_ORIGINS` (за замовчуванням
`http://127.0.0.1:8000` і `http://localhost:8000`). Шаблон `*` не
використовується, `allow_credentials=True` працює тільки з явним
списком Origin.

## Санітизація

`security/sanitizer.py` викликає `bleach.clean(..., tags=[], strip=True)`
і застосовується до імені користувача під час реєстрації та входу.
Коментарі зберігаються в БД уже очищеними; список, зміна й видалення
обмежені власником запису. Для демонстрації є захищений маршрут
`POST /api/v1/comments/preview`: він повертає і оригінал, і очищений
варіант.

Приклад:

```json
{"title": "<b>Звіт</b>", "comment": "<script>alert('XSS')</script>"}
```

```json
{"original": {"title": "<b>Звіт</b>", "comment": "<script>alert('XSS')</script>"},
 "sanitized": {"title": "Звіт", "comment": "alert('XSS')"}}
```

## Як перевірити

1. Заголовки:

```powershell
curl.exe -I http://localhost:8000/
curl.exe -I http://localhost:8000/api/docs
```

2. Cookie: увійти на <http://localhost:8000/>, відкрити DevTools →
   Application → Cookies. Переконатися, що `vault_access` має
   `HttpOnly`, `Secure`, `SameSite=Strict`.

3. CSP: у консолі DevTools виконати

```js
const s = document.createElement("script");
s.textContent = "alert('XSS')";
document.head.append(s);
```

Очікування: `Refused to execute inline script…` і жодного `alert`.

4. Санітизація: у Scalar виконати `POST /api/v1/comments/preview` з
   XSS-пейлоадом і порівняти `original` та `sanitized`.

5. CORS:

```powershell
curl.exe -i -X OPTIONS http://localhost:8000/api/v1/accounts/login `
  -H "Origin: http://evil.example" `
  -H "Access-Control-Request-Method: POST"
```

Очікування: у відповіді немає `Access-Control-Allow-Origin`.
