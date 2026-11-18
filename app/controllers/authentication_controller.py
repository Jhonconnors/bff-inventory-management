"""Endpoints de autenticación."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.exceptions import UnauthorizedError
from app.core.security import get_current_user, oauth2_scheme, revoke_token, verify_token
from app.database import get_db
from app.models.entities import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.entities import AuthenticatedUserRead, LoginRequest, LoginResponse, RefreshRequest
from app.services.authentication_service import AuthenticationService

router = APIRouter(prefix="/authentication", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(get_db)):
    return AuthenticationService(UsuarioRepository(session)).login(payload.correo, payload.password)


@router.post("/refresh", response_model=LoginResponse)
def refresh(payload: RefreshRequest, session: Session = Depends(get_db)):
    return AuthenticationService(UsuarioRepository(session)).refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(payload: RefreshRequest, access_token: str = Depends(oauth2_scheme), user: Usuario = Depends(get_current_user)):
    refresh_payload = verify_token(payload.refresh_token, expected_type="refresh")
    if refresh_payload["sub"] != str(user.id_usuario):
        raise UnauthorizedError("El refresh token no corresponde al usuario autenticado")
    revoke_token(access_token, expected_type="access")
    revoke_token(payload.refresh_token, expected_type="refresh")
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=AuthenticatedUserRead)
def me(user: Usuario = Depends(get_current_user)):
    return user