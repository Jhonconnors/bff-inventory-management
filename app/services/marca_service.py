"""Casos de uso para marcas."""

from app.repositories.marca_repository import MarcaRepository
from app.services.catalog_service import CatalogService


class MarcaService(CatalogService):
    def __init__(self, session):
        super().__init__(MarcaRepository(session), "id_marca")