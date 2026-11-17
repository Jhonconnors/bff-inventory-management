"""Repositorio de estados de equipo."""

from sqlalchemy import select

from app.models.entities import EstadoEquipo
from app.repositories.base import BaseRepository


class EstadoEquipoRepository(BaseRepository[EstadoEquipo]):
    def __init__(self, session):
        super().__init__(session, EstadoEquipo, "id_estado")

    def by_name(self, name: str) -> EstadoEquipo | None:
        return self.session.scalar(select(EstadoEquipo).where(EstadoEquipo.nombre.ilike(name)))