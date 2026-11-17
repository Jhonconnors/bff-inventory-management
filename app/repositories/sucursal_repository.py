"""Repositorio de sucursales."""

from app.models.entities import Sucursal
from app.repositories.base import BaseRepository


class SucursalRepository(BaseRepository[Sucursal]):
    def __init__(self, session):
        super().__init__(session, Sucursal, "id_sucursal")