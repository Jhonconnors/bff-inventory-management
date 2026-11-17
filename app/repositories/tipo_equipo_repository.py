"""Repositorio de tipos de equipo."""

from app.models.entities import TipoEquipo
from app.repositories.base import BaseRepository


class TipoEquipoRepository(BaseRepository[TipoEquipo]):
    def __init__(self, session):
        super().__init__(session, TipoEquipo, "id_tipo")