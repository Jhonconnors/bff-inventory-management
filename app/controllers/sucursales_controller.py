"""Endpoints CRUD de sucursales."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import CatalogCreate, SucursalRead
from app.services.sucursal_service import SucursalService

router = build_catalog_router("sucursales", "Sucursales", SucursalService, CatalogCreate, SucursalRead, "id_sucursal")