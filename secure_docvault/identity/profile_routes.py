"""Захищений профіль користувача."""

from fastapi import APIRouter, Depends

from .guard import current_claims

router = APIRouter(prefix="/api/v1/user", tags=["Профіль"])


@router.get("/profile", summary="Профіль поточного користувача")
def profile(claims: dict = Depends(current_claims)) -> dict:
    return {
        "ok": True,
        "profile": {
            "user_id": claims.get("sub"),
            "username": claims.get("username"),
            "role": claims.get("role"),
        },
    }
