"""Casos de uso para administración de usuarios."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.entities import Activo, BitacoraAuditoria, Rol, Usuario
from app.repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self.repository = repository
        self.session = repository.session

    def list(self, limit: int, offset: int, include_inactive: bool = False):
        filters = None if include_inactive else {"activo": True}
        return self.repository.list(limit, offset, filters)

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
        user = self.repository.get_or_raise(user_id)
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

    def delete(self, user_id: int, actor_id: int) -> None:
        if user_id == actor_id:
            raise ConflictError("No puedes eliminar la cuenta con la que iniciaste sesión")

        user = self.repository.get_or_raise(user_id)
        has_audit_events = self.session.scalar(
            select(BitacoraAuditoria.id_evento)
            .where(BitacoraAuditoria.id_usuario == user_id)
            .limit(1)
        )
        if has_audit_events is not None:
            raise ConflictError(
                "No se puede eliminar este usuario porque tiene eventos en la bitácora; desactívalo para conservar el historial"
            )

        has_assigned_assets = self.session.scalar(
            select(Activo.id_activo)
            .where(Activo.id_usuario == user_id)
            .limit(1)
        )
        if has_assigned_assets is not None:
            raise ConflictError(
                "No se puede eliminar este usuario porque tiene activos asignados; cambia o retira la asignación primero"
            )

        try:
            self.repository.delete(user)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("No se puede eliminar este usuario porque está referenciado") from exc
        except Exception:
            self.session.rollback()
            raise