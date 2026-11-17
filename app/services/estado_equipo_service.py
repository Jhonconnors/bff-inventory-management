"""Casos de uso para estados de equipo."""

from app.repositories.estado_equipo_repository import EstadoEquipoRepository
from app.services.catalog_service import CatalogService


class EstadoEquipoService(CatalogService):
    def __init__(self, session):
        super().__init__(EstadoEquipoRepository(session), "id_estado")