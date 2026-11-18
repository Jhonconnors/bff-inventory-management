"""Casos de uso de autenticación."""

import logging

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, create_refresh_token, revoke_token, verify_password, verify_token
from app.repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


class AuthenticationService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self.repository = repository

    def login(self, correo: str, password: str) -> dict[str, str]:
        user = self.repository.by_email(correo)
        if user is None or not user.activo or not verify_password(password, user.password_hash):
            logger.warning("Intento de autenticación fallido para %s", correo)
            raise UnauthorizedError("Credenciales inválidas")
        return {"access_token": create_access_token(user.id_usuario), "refresh_token": create_refresh_token(user.id_usuario), "token_type": "bearer"}

    def refresh(self, token: str) -> dict[str, str]:
        payload = verify_token(token, expected_type="refresh")
        user = self.repository.get(int(payload["sub"]))
        if user is None or not user.activo:
            raise UnauthorizedError("Usuario no disponible")
        revoke_token(token, expected_type="refresh")
        return {"access_token": create_access_token(user.id_usuario), "refresh_token": create_refresh_token(user.id_usuario), "token_type": "bearer"}