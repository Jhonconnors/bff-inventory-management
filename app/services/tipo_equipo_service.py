"""Casos de uso para tipos de equipo."""

from app.repositories.tipo_equipo_repository import TipoEquipoRepository
from app.services.catalog_service import CatalogService


class TipoEquipoService(CatalogService):
    def __init__(self, session):
        super().__init__(TipoEquipoRepository(session), "id_tipo")