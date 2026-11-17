"""Casos de uso para administración de usuarios."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.entities import Rol, Usuario
from app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self.repository = repository
        self.session = repository.session

    def list(self, limit: int, offset: int):
        return self.repository.list(limit, offset, {"activo": True})

    def get(self, user_id: int) -> Usuario:
        user = self.repository.get_or_raise(user_id)
        if not user.activo:
            raise NotFoundError(f"Usuario {user_id} no existe")
        return user

    def create(self, values: dict):
        if self.session.get(Rol, values["id_rol"]) is None:
            raise NotFoundError("El rol indicado no existe")
        values["correo"] = values["correo"].lower()
        values["password_hash"] = hash_password(values.pop("password"))
        try:
            user = self.repository.add(values)
            self.session.commit()
            return user
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("El correo ya está registrado") from exc

    def update(self, user_id: int, values: dict):
        user = self.get(user_id)
        if self.session.get(Rol, values["id_rol"]) is None:
            raise NotFoundError("El rol indicado no existe")
        values["correo"] = values["correo"].lower()
        password = values.pop("password", None)
        if password:
            values["password_hash"] = hash_password(password)
        try:
            updated = self.repository.update(user, values)
            self.session.commit()
            return updated
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("El correo ya está registrado") from exc

    def set_active(self, user_id: int, active: bool):
        user = self.repository.get_or_raise(user_id)
        user.activo = active
        self.session.commit()
        return user

    def delete(self, user_id: int) -> None:
        self.set_active(user_id, False)