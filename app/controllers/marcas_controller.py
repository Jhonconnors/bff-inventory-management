"""Endpoints CRUD de marcas."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import CatalogCreate, MarcaRead
from app.services.marca_service import MarcaService

router = build_catalog_router("marcas", "Marcas", MarcaService, CatalogCreate, MarcaRead, "id_marca")