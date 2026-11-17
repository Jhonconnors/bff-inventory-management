"""Repositorio de roles."""

from app.models.entities import Rol
from app.repositories.base import BaseRepository


class RolRepository(BaseRepository[Rol]):
    def __init__(self, session):
        super().__init__(session, Rol, "id_rol")