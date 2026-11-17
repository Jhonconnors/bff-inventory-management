"""Casos de uso para roles."""

from app.models.entities import Rol
from app.repositories.rol_repository import RolRepository
from app.services.base import CRUDService


class RolService(CRUDService):
    def __init__(self, session):
        super().__init__(RolRepository(session), "id_rol")