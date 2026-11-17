"""Casos de uso para departamentos."""

from app.repositories.departamento_repository import DepartamentoRepository
from app.services.catalog_service import CatalogService


class DepartamentoService(CatalogService):
    def __init__(self, session):
        super().__init__(DepartamentoRepository(session), "id_departamento")