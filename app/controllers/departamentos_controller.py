"""Endpoints CRUD de departamentos."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import CatalogCreate, DepartamentoRead
from app.services.departamento_service import DepartamentoService

router = build_catalog_router("departamentos", "Departamentos", DepartamentoService, CatalogCreate, DepartamentoRead, "id_departamento")