"""Endpoints CRUD de tipos de equipo."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import CatalogCreate, TipoEquipoRead
from app.services.tipo_equipo_service import TipoEquipoService

router = build_catalog_router("tipos-equipo", "TiposEquipo", TipoEquipoService, CatalogCreate, TipoEquipoRead, "id_tipo")