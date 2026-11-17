"""Repositorio de usuarios."""

from sqlalchemy import select

from app.models.entities import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session):
        super().__init__(session, Usuario, "id_usuario")

    def by_email(self, correo: str) -> Usuario | None:
        return self.session.scalar(select(Usuario).where(Usuario.correo == correo.lower()))