"""Repositorio de modelos de equipo."""

from app.models.entities import Modelo
from app.repositories.base import BaseRepository


class ModeloRepository(BaseRepository[Modelo]):
    def __init__(self, session):
        super().__init__(session, Modelo, "id_modelo")