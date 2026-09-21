from dto.auth_dto import (
    AuthResponseDTO,
    LoginRequestDTO,
    MeResponseDTO,
    RefreshRequestDTO,
    RefreshResponseDTO,
    RegisterRequestDTO,
)
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from handler import auth_handler

router = APIRouter(tags=["Auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> MeResponseDTO:
    return auth_handler.get_me(credentials.credentials)


@router.post("/auth/register", response_model=AuthResponseDTO)
async def register(request: RegisterRequestDTO):
    return auth_handler.register(request)


@router.post("/auth/login", response_model=AuthResponseDTO)
async def login(request: LoginRequestDTO):
    return auth_handler.login(request)


@router.get("/auth/me", response_model=MeResponseDTO)
async def me(user: MeResponseDTO = Depends(get_current_user)):
    return user


@router.post("/auth/refresh", response_model=RefreshResponseDTO)
async def refresh(request: RefreshRequestDTO):
    return auth_handler.refresh(request)
