"""Rate limiting, WAF та Greylist."""

from __future__ import annotations


def wrong_login(client):
    return client.post(
        "/api/v1/accounts/login",
        json={"username": "nobody", "password": "WrongPass1!"},
    )


def test_login_limit_returns_429_with_retry_after(client):
    for _ in range(5):
        assert wrong_login(client).status_code == 401

    response = wrong_login(client)

    assert response.status_code == 429
    assert response.headers["retry-after"].isdigit()
    assert response.json()["error"]["code"] == "rate_limited"


def test_general_api_limit_is_sixty(client):
    for _ in range(60):
        assert client.get("/api/v1/user/profile").status_code == 401

    response = client.get("/api/v1/user/profile")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "rate_limited"


def test_path_traversal_is_blocked_and_ip_banned(client):
    attack = client.get("/api/v1/user/profile?file=../../etc/passwd")

    assert attack.status_code == 403
    assert attack.json()["error"]["code"] == "waf_blocked"

    after = client.get("/api/v1/user/profile")

    assert after.status_code == 403
    assert after.json()["error"]["code"] == "ip_banned"


def test_sql_injection_in_body_is_blocked(client):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": "' OR '1'='1", "password": "x"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "waf_blocked"


def test_command_injection_is_blocked(client):
    response = client.get("/api/v1/user/profile?cmd=/bin/sh")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "waf_blocked"


def test_xss_text_is_not_blocked_by_waf(client, member):
    response = client.post(
        "/api/v1/comments/preview",
        json={"title": "Тест", "comment": "<script>alert(1)</script>"},
        headers={"Cookie": "vault_access="},
    )

    # Без токена буде 401, але не 403: WAF не чіпає XSS-текст.
    assert response.status_code == 401
