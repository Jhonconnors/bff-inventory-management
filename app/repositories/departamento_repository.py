"""Repositorio de departamentos."""

from app.models.entities import Departamento
from app.repositories.base import BaseRepository


class DepartamentoRepository(BaseRepository[Departamento]):
    def __init__(self, session):
        super().__init__(session, Departamento, "id_departamento")