"""Consultas de persistencia para activos tecnológicos."""

from sqlalchemy import or_, select

from app.models.entities import Activo
from app.repositories.base import BaseRepository


class ActivoRepository(BaseRepository[Activo]):
    def __init__(self, session):
        super().__init__(session, Activo, "id_activo")

    def duplicate(self, placa: str, serie: str, exclude_id: int | None = None) -> str | None:
        conditions = [Activo.placa == placa, Activo.serie == serie]
        statement = select(Activo).where(or_(*conditions))
        if exclude_id is not None:
            statement = statement.where(Activo.id_activo != exclude_id)
        existing = self.session.scalar(statement)
        if existing is None:
            return None
        return "placa" if existing.placa == placa else "serie"

    def search(self, filters: dict, limit: int, offset: int) -> tuple[list[Activo], int]:
        return self.list(limit, offset, filters)