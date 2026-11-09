# Secure DocVault

Корпоративне сховище конфіденційних документів: реєстрація та вхід
працівників, зберігання облікових записів у SQLite, стійке хешування
паролів, захист від SQL-ін'єкцій, шифрування файлів AES-256-GCM та
електронний цифровий підпис RSA-PSS.

Клієнт — вебзастосунок (HTML, CSS, нативний JavaScript). Сервер віддає
і REST API, і сам інтерфейс із профілем, документами та коментарями.
## Запуск

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py
```

* Інтерфейс: <http://localhost:8000/>
* Документація API (Scalar): <http://localhost:8000/api/docs>

## Налаштування

Скопіюйте `.env.example` у `.env`, щоб змінити адресу, шлях до бази,
фактор хешування, секрети JWT/файлів/ЕЦП (`VAULT_*_KEY`), прапорець
`VAULT_COOKIE_SECURE` або список дозволених Origin (`VAULT_CORS_ORIGINS`).

## API
| Метод | Шлях | Призначення |
|---|---|---|
| POST | `/api/v1/accounts/register` | створити обліковий запис |
| POST | `/api/v1/accounts/login` | увійти, отримати токени й cookie |
| POST | `/api/v1/auth/refresh` | оновити пару токенів |
| GET | `/api/v1/user/profile` | профіль за токеном або cookie |
| GET | `/api/v1/documents` | мої документи |
| POST | `/api/v1/documents/upload` | завантажити й зашифрувати |
| GET/DELETE | `/api/v1/documents/{id}` | скачати / видалити |
| GET/POST | `/api/v1/documents/{id}/comments` | коментарі до документа |
| GET/POST | `/api/v1/signing/keys` | інформація / генерація ключів ЕЦП |
| GET | `/api/v1/signing/keys/public` | експорт відкритого ключа X.509 |
| POST | `/api/v1/signing/keys/export` | приватний ключ PKCS#8 із паролем |

Помилки мають єдиний формат `{ok, error{code, message, fields}}`; сервер повертає всі зауваження одразу.
## Захист

* bcrypt із фактором 12 та унікальною сіллю на кожен запис;
* лише параметризовані SQL-запити (`?`), без склеювання рядків;
* однакове повідомлення для невідомого користувача та невірного пароля;
* JWT (HS256): access 15 хв, refresh 7 діб, ротація, заборона `alg: none`;
* санітизація користувацького тексту (bleach) проти XSS;
* коментарі зберігаються очищеними й доступні лише власнику;
* AES-256-GCM для файлів: IV + Tag + шифротекст, AAD на документ;
* ЕЦП RSA-2048/PSS/SHA-256: підпис під час завантаження, перевірка під
  час скачування, `409 signature_invalid` для підробленого підпису;
* cookie `HttpOnly`, `Secure`, `SameSite=Strict`;
* CSP без `unsafe-inline` для застосунку, HSTS, `nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy`;
* CORS лише для дозволених Origin, без `*`;
* rate limiting: 5/хв для входу, 60/хв для API, `429` + `Retry-After`;
* WAF: path traversal, SQLi та command injection → `403` і Greylist.

## Перевірка

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

Демонстрація для протоколу (потрібен запущений сервер):

```powershell
python tools/jwt_demo.py
python tools/stress_check.py; python tools/injection_check.py; python tools/db_report.py; python tools/signature_check.py
```

## Структура

```text
manage.py                  запуск сервера
secure_docvault/
  factory.py               складання FastAPI-застосунку
  settings/                конфігурація з .env
  persistence/             SQLite: з'єднання, схема
  identity/                облікові записи, хешування, JWT
  security/                санітизація тексту і AES-256-GCM
  signing/                 ключі ЕЦП, RSA-PSS, підпис і верифікація
  comments/                коментарі до документів
  documents/               завантаження, шифрування, скачування
  transport/               помилки, заголовки, cookie, WAF і ліміти
  site/                    вебклієнт і довідка API
frontend/                  каркас, власні SVG, стилі, компоненти
tests/ і tools/            pytest та скрипти для звіту
```

Принципи архітектури та межа у 100 рядків на файл — у
[`docs/architecture.md`](docs/architecture.md). Деталі — у
[`docs/security.md`](docs/security.md), [`docs/client-security.md`](docs/client-security.md),
[`docs/network-security.md`](docs/network-security.md), [`docs/file-encryption.md`](docs/file-encryption.md),
[`docs/digital-signature.md`](docs/digital-signature.md), [`docs/testing.md`](docs/testing.md),
[`docs/testing-jwt.md`](docs/testing-jwt.md).
