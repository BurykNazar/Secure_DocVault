# Перевірка JWT

Дії виконуються після запуску `python manage.py` і реєстрації
користувача. Приклади — для PowerShell.

## 1. Отримання пари токенів

```powershell
$login = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/accounts/login `
  -ContentType application/json `
  -Body '{"username":"nazar_buryk","password":"Dossier2026!"}'

$login.access_token
$login.refresh_token
```

Очікування: `token_type = bearer`, обидва токени непорожні.

## 2. Будова токена

Розділити access-токен на три частини (Header.Payload.Signature) і
показати декодований payload: `sub`, `username`, `role`, `type`,
`jti`, `iat`, `exp`. Дані не зашифровані — лише підписані.

## 3. Захищений профіль

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/user/profile `
  -Headers @{ Authorization = "Bearer $($login.access_token)" }
```

Очікування: `200` і `profile.username`.

## 4. Без токена

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/v1/user/profile
```

Очікування: `401`, код `invalid_token`.

## 5. Підміна ролі

Взяти payload, змінити `role` на `admin`, залишити старий підпис і
надіслати токен. Очікування: `401` — підпис не збігається.

## 6. Ротація refresh-токена

```powershell
$pair = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/auth/refresh `
  -ContentType application/json `
  -Body (@{ refresh_token = $login.refresh_token } | ConvertTo-Json)

$pair.access_token
$pair.refresh_token
```

Нова пара відрізняється від попередньої. Повторний виклик із **старим**
`$login.refresh_token` повертає `401` з кодом `token_reuse`.
