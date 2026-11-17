"""Casos de uso para modelos."""

from app.repositories.modelo_repository import ModeloRepository
from app.services.catalog_service import CatalogService


class ModeloService(CatalogService):
    def __init__(self, session):
        super().__init__(ModeloRepository(session), "id_modelo")