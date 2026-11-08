# Secure DocVault

Корпоративне сховище конфіденційних документів: реєстрація та вхід
працівників, зберігання облікових записів у SQLite, стійке хешування
паролів і захист від SQL-ін'єкцій.

Клієнтська частина — вебзастосунок (HTML, CSS, нативний JavaScript).
Сервер віддає і REST API, і сам інтерфейс, тому окремого десктопного
клієнта не потрібно.

## Запуск

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py
```

* Інтерфейс: <http://127.0.0.1:8000/>
* Документація API: <http://127.0.0.1:8000/api/docs>

Linux/macOS: `source venv/bin/activate` замість `Activate.ps1`.

## Налаштування

Скопіюйте `.env.example` у `.env`, якщо потрібно змінити адресу, шлях до
бази або фактор трудомісткості хешування.

## API

| Метод | Шлях | Призначення |
|---|---|---|
| POST | `/api/v1/accounts/register` | створити обліковий запис |
| POST | `/api/v1/accounts/login` | увійти |

Помилки мають єдиний вигляд:

```json
{
  "ok": false,
  "error": {
    "code": "validation_failed",
    "message": "Перевірте введені дані",
    "fields": {"password": ["Додайте цифру"]}
  }
}
```

Сервер повертає всі зауваження до форми одразу, а клієнт лише показує
їх біля відповідних полів.

## Захист

* bcrypt із фактором 12 та унікальною сіллю на кожен запис;
* лише параметризовані SQL-запити (`?`), без склеювання рядків;
* однакове повідомлення для невідомого користувача та невірного пароля;
* перевірка складності пароля та обмеження довжини 72 байтами;
* валідація імені користувача й електронної адреси на сервері.

Докладніше: [`docs/security.md`](docs/security.md).

## Перевірка

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

Демонстрація SQL-ін'єкції (потрібен запущений сервер) та вміст таблиці
`users` для протоколу:

```powershell
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
  identity/                облікові записи: правила, хешування, сервіси
  transport/               єдиний формат помилок
  site/                    віддача вебклієнта
frontend/                  каркас, власні SVG, стилі, компоненти
tests/                     pytest
tools/                     допоміжні скрипти для звіту
```

Принципи архітектури та межа у 100 рядків на файл — у
[`docs/architecture.md`](docs/architecture.md), порядок перевірки — у
[`docs/testing.md`](docs/testing.md).
