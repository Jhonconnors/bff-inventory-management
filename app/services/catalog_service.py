"""Servicio CRUD base para catálogos con relaciones opcionales."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.models.entities import Marca
from app.services.base import CRUDService


class CatalogService(CRUDService):
    def create(self, values: dict):
        self._validate(values)
        return super().create(values)

    def update(self, entity_id: int, values: dict):
        self._validate(values)
        return super().update(entity_id, values)

    def _validate(self, values: dict) -> None:
        if "id_marca" in values and self.session.get(Marca, values["id_marca"]) is None:
            raise NotFoundError("La marca indicada no existe")