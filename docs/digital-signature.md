# Електронний цифровий підпис

## Алгоритм

Кожен користувач отримує пару RSA-2048 з публічною експонентою
`65537`. Підпис створюється за схемою **RSA-PSS** з `MGF1(SHA-256)`
та максимальною довжиною солі, тому підпис імовірнісний: для одного
й того самого документа щоразу виходить інший результат.

Підписується не сам файл, а його дайджест SHA-256, який RSA-PSS
обчислює всередині. Для перевірки потрібні лише відкритий ключ,
документ і підпис.

## Ключі

- приватний ключ зберігається в БД **зашифрованим** AES-256-GCM;
- ключ шифрування — `VAULT_SIGNING_KEY` (64 hex-символи, 256 біт),
  окремий від `VAULT_FILE_KEY`;
- AAD приватного ключа: `docvault|signing-key|v1`;
- експорт приватного ключа — PKCS#8 із парольною фразою (мінімум 8
  символів), відкритого — X.509 PEM.

## Таблиці

```text
user_signing_keys     user_id, algorithm, public_key_pem,
                      private_key_encrypted, key_fingerprint, created_at
document_signatures   document_id, signer_id, algorithm,
                      signature_b64, public_key_fingerprint, signed_at
```

## Маршрути

| Метод | Шлях | Що робить |
|---|---|---|
| GET | `/api/v1/signing/keys` | інформація про ключ або `null` |
| POST | `/api/v1/signing/keys` | створює пару ключів |
| GET | `/api/v1/signing/keys/public` | віддає X.509 PEM |
| POST | `/api/v1/signing/keys/export` | віддає PKCS#8 PEM із паролем |

Завантаження документа автоматично створює ключ (якщо його ще немає)
і зберігає підпис. Скачування перевіряє підпис і повертає заголовки:

```text
X-Signature-Status: Signed & Verified
X-Signature-Algorithm: RSA-PSS-SHA256
X-Signature-Fingerprint: <64 hex>
X-Signer: <username>
X-Signed-At: <timestamp>
```

Якщо підпис не збігається з вмістом, файл не видається:
`409 signature_invalid`. Документи, завантажені до ЛР №6, мають статус
`Unsigned` і не блокуються.

## Перевірка

```powershell
python tools/signature_check.py
```

Скрипт генерує ключі, підписує рядок, перевіряє його, підміняє слово
`APPROVED` на `REJECTED` і показує, що підпис стає недійсним. Він також
перевіряє експорт/імпорт X.509 та PKCS#8.

Автоматичні тести: `tests/test_signing_keys.py` і
`tests/test_signatures.py` (генерація ключів, експорт із паролем,
підписування, заголовки скачування, підроблений підпис).
