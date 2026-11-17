"""Autenticación JWT y dependencias de autorización por rol."""

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.entities import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/authentication/login")


def hash_password(password: str) -> str:
	"""Genera un hash bcrypt no reversible."""
	return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
	"""Compara una contraseña con su hash almacenado."""
	try:
		return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
	except (ValueError, TypeError):
		return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
	"""Firma un access token JWT."""
	expires = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
	return jwt.encode({"sub": str(subject), "type": "access", "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
	"""Firma un refresh token JWT de duración extendida."""
	expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
	return jwt.encode({"sub": str(subject), "type": "refresh", "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
	"""Valida firma, vencimiento y propósito del token."""
	try:
		payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
	except JWTError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"}) from exc
	if payload.get("type") != expected_type or not payload.get("sub"):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
	return payload


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)) -> Usuario:
	"""Resuelve el usuario activo asociado al access token."""
	payload = verify_token(token)
	try:
		user_id = int(payload["sub"])
	except (TypeError, ValueError) as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from exc
	user = session.get(Usuario, user_id)
	if user is None or not user.activo:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no disponible")
	return user


def require_roles(*roles: str) -> Callable[..., Usuario]:
	"""Crea una dependencia que limita el acceso a los roles indicados."""
	def role_dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
		if user.rol.nombre not in roles:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
		return user
	return role_dependency
