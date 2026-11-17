"""Repositorio de marcas."""

from app.models.entities import Marca
from app.repositories.base import BaseRepository


class MarcaRepository(BaseRepository[Marca]):
    def __init__(self, session):
        super().__init__(session, Marca, "id_marca")