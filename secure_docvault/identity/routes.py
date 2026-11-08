"""HTTP-маршрути облікових записів."""

from fastapi import APIRouter, Request, status

from .authentication import sign_in
from .models import SignIn, SignUp
from .registration import sign_up

router = APIRouter(prefix="/api/v1/accounts", tags=["Облікові записи"])


def _client(request: Request) -> str:
    """IP для журналу. X-Forwarded-For поки не довіряємо: без
    перевіреного reverse-proxy його легко підробити."""
    return request.client.host if request.client else "unknown"


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Створити обліковий запис")
def register(payload: SignUp, request: Request) -> dict:
    account = sign_up(payload, _client(request))
    return {
        "ok": True,
        "message": "Обліковий запис створено.",
        "account": account,
    }


@router.post("/login", summary="Увійти в обліковий запис")
def login(payload: SignIn, request: Request) -> dict:
    account = sign_in(payload, _client(request))
    return {
        "ok": True,
        "message": f"Вітаємо, {account['username']}!",
        "account": account,
    }
