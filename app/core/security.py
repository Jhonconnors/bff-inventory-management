"""Autenticación JWT y dependencias de autorización por rol."""

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Callable
from uuid import uuid4

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.entities import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/authentication/login")
_PASSWORD_HASH_PREFIX = "$bcrypt-sha256$v1$"
_revoked_tokens: dict[str, int] = {}
_revoked_tokens_lock = Lock()


def _password_bytes(password: str) -> bytes:
	"""Prehashea contraseñas largas para no exceder el límite de bcrypt."""
	material = b"bcrypt-sha256-v1:" + password.encode("utf-8")
	return base64.b64encode(hashlib.sha256(material).digest())


def _token_fingerprint(token: str) -> str:
	"""Devuelve un identificador irreversible del JWT para la lista de revocación."""
	return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_token_revoked(token: str, now: int) -> bool:
	fingerprint = _token_fingerprint(token)
	with _revoked_tokens_lock:
		for revoked_fingerprint, expiration in tuple(_revoked_tokens.items()):
			if expiration <= now:
				del _revoked_tokens[revoked_fingerprint]
		return fingerprint in _revoked_tokens


def hash_password(password: str) -> str:
	"""Genera un hash bcrypt versionado compatible con contraseñas de hasta 255 caracteres."""
	hashed = bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("ascii")
	return f"{_PASSWORD_HASH_PREFIX}{hashed}"


def verify_password(password: str, password_hash: str) -> bool:
	"""Verifica hashes nuevos y hashes bcrypt directos ya almacenados."""
	try:
		if password_hash.startswith(_PASSWORD_HASH_PREFIX):
			candidate = _password_bytes(password)
			existing_hash = password_hash[len(_PASSWORD_HASH_PREFIX):].encode("ascii")
		else:
			candidate = password.encode("utf-8")
			existing_hash = password_hash.encode("ascii")
		return bcrypt.checkpw(candidate, existing_hash)
	except (ValueError, TypeError):
		return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
	"""Firma un access token JWT."""
	expires = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
	return jwt.encode({"sub": str(subject), "type": "access", "jti": uuid4().hex, "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
	"""Firma un refresh token JWT de duración extendida."""
	expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
	return jwt.encode({"sub": str(subject), "type": "refresh", "jti": uuid4().hex, "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
	"""Valida firma, vencimiento y propósito del token."""
	try:
		payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
	except JWTError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"}) from exc
	if payload.get("type") != expected_type or not payload.get("sub"):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
	now = int(datetime.now(timezone.utc).timestamp())
	if _is_token_revoked(token, now):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revocado", headers={"WWW-Authenticate": "Bearer"})
	return payload


def revoke_token(token: str, expected_type: str) -> None:
	"""Revoca un JWT hasta su expiración en el proceso actual."""
	payload = verify_token(token, expected_type)
	expiration = payload.get("exp")
	if not isinstance(expiration, (int, float)):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
	with _revoked_tokens_lock:
		_revoked_tokens[_token_fingerprint(token)] = int(expiration)


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


def require_authenticated(user: Usuario = Depends(get_current_user)) -> Usuario:
	"""Permite consultar módulos generales a cualquier usuario autenticado."""
	return user
