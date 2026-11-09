"""HTTP-маршрути облікових записів."""

from fastapi import APIRouter, Response, status

from ..transport.cookies import set_access_cookie
from .authentication import sign_in
from .models import SignIn, SignUp
from .registration import sign_up
from .tokens import issue_pair

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
def login(payload: SignIn, response: Response) -> dict:
    account = sign_in(payload)
    tokens = issue_pair(account)
    set_access_cookie(response, tokens["access_token"])

    return {
        "ok": True,
        "message": f"Вітаємо, {account['username']}!",
        "account": account,
        **tokens,
    }
