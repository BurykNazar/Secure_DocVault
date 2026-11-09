# Secure DocVault

Корпоративне сховище конфіденційних документів: реєстрація та вхід
працівників, зберігання облікових записів у SQLite, стійке хешування
паролів і захист від SQL-ін'єкцій.

Клієнт — вебзастосунок (HTML, CSS, нативний JavaScript). Сервер віддає
і REST API, і сам інтерфейс. Після входу доступна панель «Мої коментарі»:
створення, редагування й видалення лише власних записів.

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

Скопіюйте `.env.example` у `.env`, якщо потрібно змінити адресу, шлях
до бази, фактор хешування, секрет JWT (`VAULT_JWT_SECRET`), прапорець
`VAULT_COOKIE_SECURE` або список дозволених Origin (`VAULT_CORS_ORIGINS`).

## API

| Метод | Шлях | Призначення |
|---|---|---|
| POST | `/api/v1/accounts/register` | створити обліковий запис |
| POST | `/api/v1/accounts/login` | увійти, отримати токени й cookie |
| POST | `/api/v1/auth/refresh` | оновити пару токенів |
| GET | `/api/v1/user/profile` | профіль за токеном або cookie |
| GET/POST | `/api/v1/comments` | мої коментарі / додати |
| PUT/DELETE | `/api/v1/comments/{id}` | змінити / видалити свій |
| POST | `/api/v1/comments/preview` | очистити текст від HTML/JS |

Помилки мають єдиний формат `{ok, error{code, message, fields}}`, і
сервер повертає всі зауваження до форми одразу.

## Захист

* bcrypt із фактором 12 та унікальною сіллю на кожен запис;
* лише параметризовані SQL-запити (`?`), без склеювання рядків;
* однакове повідомлення для невідомого користувача та невірного пароля;
* JWT (HS256): access — 15 хв, refresh — 7 діб, ротація та заборона
  `alg: none`;
* санітизація користувацького тексту (bleach) проти XSS;
* коментарі зберігаються очищеними й доступні лише власнику;
* cookie `HttpOnly`, `Secure`, `SameSite=Strict`;
* CSP без `unsafe-inline` для застосунку, HSTS, `nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy`;
* CORS лише для дозволених Origin, без `*`.

Докладніше: [`docs/security.md`](docs/security.md) і
[`docs/client-security.md`](docs/client-security.md).

## Перевірка

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

Демонстрація для протоколу (потрібен запущений сервер):

```powershell
python tools/jwt_demo.py
python tools/injection_check.py
python tools/db_report.py
```

## Структура

```text
manage.py                  запуск сервера
secure_docvault/
  factory.py               складання FastAPI-застосунку
  settings/                конфігурація з .env
  persistence/             SQLite: з'єднання, схема
  identity/                облікові записи, хешування, JWT
  security/                санітизація тексту
  comments/                коментарі: CRUD, лише свої
  transport/               помилки, заголовки, cookie
  site/                    вебклієнт і довідка API
frontend/                  каркас, власні SVG, стилі, компоненти
tests/                     pytest
tools/                     допоміжні скрипти для звіту
```

Принципи архітектури та межа у 100 рядків на файл — у
[`docs/architecture.md`](docs/architecture.md). Порядок перевірки — у
[`docs/testing.md`](docs/testing.md), [`docs/testing-jwt.md`](docs/testing-jwt.md)
та [`docs/client-security.md`](docs/client-security.md).
