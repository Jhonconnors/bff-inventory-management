"""Casos de uso para sucursales."""

from app.repositories.sucursal_repository import SucursalRepository
from app.services.catalog_service import CatalogService


class SucursalService(CatalogService):
    def __init__(self, session):
        super().__init__(SucursalRepository(session), "id_sucursal")