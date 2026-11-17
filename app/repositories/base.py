"""Operaciones de persistencia reutilizables para repositorios concretos."""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Acceso de datos CRUD sin reglas de negocio."""

    def __init__(self, session: Session, model: type[ModelT], id_field: str) -> None:
        self.session = session
        self.model = model
        self.id_field = id_field

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def get_or_raise(self, entity_id: int) -> ModelT:
        entity = self.get(entity_id)
        if entity is None:
            raise NotFoundError(f"{self.model.__name__} {entity_id} no existe")
        return entity

    def list(self, limit: int = 50, offset: int = 0, filters: dict[str, Any] | None = None) -> tuple[list[ModelT], int]:
        statement = select(self.model)
        count_statement = select(func.count()).select_from(self.model)
        for field, value in (filters or {}).items():
            if value is not None and hasattr(self.model, field):
                column = getattr(self.model, field)
                statement = statement.where(column.ilike(f"%{value}%") if isinstance(value, str) else column == value)
                count_statement = count_statement.where(column.ilike(f"%{value}%") if isinstance(value, str) else column == value)
        items = list(self.session.scalars(statement.order_by(getattr(self.model, self.id_field)).limit(limit).offset(offset)).all())
        total = int(self.session.scalar(count_statement) or 0)
        return items, total

    def add(self, values: dict[str, Any]) -> ModelT:
        entity = self.model(**values)
        self.session.add(entity)
        self.session.flush()
        return entity

    def update(self, entity: ModelT, values: dict[str, Any]) -> ModelT:
        for field, value in values.items():
            setattr(entity, field, value)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()