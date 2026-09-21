from dto.auth_dto import (
    AuthResponseDTO,
    LoginRequestDTO,
    MeResponseDTO,
    RefreshRequestDTO,
    RefreshResponseDTO,
    RegisterRequestDTO,
)
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from service.supabase_client import client
from supabase import AuthApiError


def register(request: RegisterRequestDTO) -> AuthResponseDTO | JSONResponse:
    try:
        response = client.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {"data": {"display_name": request.display_name}},
            }
        )
    except AuthApiError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    if response.session is None:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": "Registered. Check your email to confirm your account before logging in."
            },
        )

    return AuthResponseDTO(
        user_id=response.user.id,
        token=response.session.access_token,
        expires_in=response.session.expires_in,
    )


def login(request: LoginRequestDTO) -> AuthResponseDTO:
    try:
        response = client.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
        )

    return AuthResponseDTO(
        user_id=response.user.id,
        token=response.session.access_token,
        expires_in=response.session.expires_in,
    )


def refresh(request: RefreshRequestDTO) -> RefreshResponseDTO:
    try:
        response = client.auth.refresh_session(request.refresh_token)
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token."
        )

    return RefreshResponseDTO(
        token=response.session.access_token,
        expires_in=response.session.expires_in,
    )


def get_me(token: str) -> MeResponseDTO:
    try:
        response = client.auth.get_user(token)
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token."
        )

    user = response.user
    return MeResponseDTO(
        user_id=user.id,
        email=user.email,
        display_name=(user.user_metadata or {}).get("display_name"),
        created_at=str(user.created_at),
    )
