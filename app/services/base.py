"""Servicios CRUD con manejo uniforme de transacciones."""

import logging
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CRUDService:
    """Reglas CRUD comunes para catálogos simples."""

    def __init__(self, repository: BaseRepository, id_field: str) -> None:
        self.repository = repository
        self.session = repository.session
        self.id_field = id_field

    def list(self, limit: int, offset: int):
        return self.repository.list(limit, offset)

    def get(self, entity_id: int):
        return self.repository.get_or_raise(entity_id)

    def create(self, values: dict[str, Any]):
        try:
            entity = self.repository.add(values)
            self.session.commit()
            return entity
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("El registro ya existe o está referenciado") from exc
        except Exception:
            self.session.rollback()
            raise

    def update(self, entity_id: int, values: dict[str, Any]):
        entity = self.repository.get_or_raise(entity_id)
        try:
            entity = self.repository.update(entity, values)
            self.session.commit()
            return entity
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("El registro ya existe o está referenciado") from exc
        except Exception:
            self.session.rollback()
            raise

    def delete(self, entity_id: int) -> None:
        entity = self.repository.get_or_raise(entity_id)
        try:
            self.repository.delete(entity)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("No se puede eliminar un registro que está en uso") from exc
        except Exception:
            self.session.rollback()
            raise