"""HTTP-маршрути облікових записів."""

from fastapi import APIRouter, status

from .authentication import sign_in
from .models import SignIn, SignUp
from .registration import sign_up

router = APIRouter(prefix="/api/v1/accounts", tags=["Облікові записи"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Створити обліковий запис",
)
def register(payload: SignUp) -> dict:
    account = sign_up(payload)
    return {
        "ok": True,
        "message": "Обліковий запис створено.",
        "account": account,
    }


@router.post("/login", summary="Увійти в обліковий запис")
def login(payload: SignIn) -> dict:
    account = sign_in(payload)
    return {
        "ok": True,
        "message": f"Вітаємо, {account['username']}!",
        "account": account,
    }
