"""Repositorio de consulta e inserción de auditoría."""

from sqlalchemy import func, select

from app.core.exceptions import BusinessRuleError
from app.models.entities import BitacoraAuditoria
from app.repositories.base import BaseRepository


class AuditoriaRepository(BaseRepository[BitacoraAuditoria]):
    def __init__(self, session):
        super().__init__(session, BitacoraAuditoria, "id_evento")

    def for_asset(self, asset_id: int, limit: int = 100, offset: int = 0):
        statement = select(BitacoraAuditoria).where(BitacoraAuditoria.id_activo == asset_id)
        count_statement = select(func.count()).select_from(BitacoraAuditoria).where(BitacoraAuditoria.id_activo == asset_id)
        items = list(self.session.scalars(statement.order_by(BitacoraAuditoria.fecha_hora.desc()).limit(limit).offset(offset)).all())
        return items, int(self.session.scalar(count_statement) or 0)

    def update(self, entity, values):
        raise BusinessRuleError("La bitácora de auditoría es inmutable")

    def delete(self, entity) -> None:
        raise BusinessRuleError("La bitácora de auditoría es inmutable")