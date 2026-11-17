"""Casos de uso de consulta de bitácora; no se ofrecen cambios ni borrados."""

from app.core.exceptions import NotFoundError
from app.repositories.auditoria_repository import AuditoriaRepository


class AuditoriaService:
    def __init__(self, repository: AuditoriaRepository) -> None:
        self.repository = repository

    def list(self, limit: int, offset: int):
        return self.repository.list(limit, offset)

    def get(self, event_id: int):
        event = self.repository.get(event_id)
        if event is None:
            raise NotFoundError(f"Evento de auditoría {event_id} no existe")
        return event