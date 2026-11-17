"""Endpoints CRUD de estados de equipo."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import CatalogCreate, EstadoEquipoRead
from app.services.estado_equipo_service import EstadoEquipoService

router = build_catalog_router("estados-equipo", "EstadosEquipo", EstadoEquipoService, CatalogCreate, EstadoEquipoRead, "id_estado")