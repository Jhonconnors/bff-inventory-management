"""Endpoints CRUD de modelos."""

from app.controllers.catalog_routes import build_catalog_router
from app.schemas.entities import ModeloCreate, ModeloRead
from app.services.modelo_service import ModeloService

router = build_catalog_router("modelos", "Modelos", ModeloService, ModeloCreate, ModeloRead, "id_modelo")