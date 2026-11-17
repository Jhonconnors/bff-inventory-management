"""Aplicación FastAPI SIGATI+."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.controllers import (
	authentication_controller,
	activos_controller,
	auditoria_controller,
	departamentos_controller,
	estados_equipo_controller,
	marcas_controller,
	modelos_controller,
	roles_controller,
	sucursales_controller,
	tipos_equipo_controller,
	usuarios_controller,
)
from app.core.config import settings
from app.core.exceptions import AppError
from app.database import Base
from app.models import entities as _entities  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.exception_handler(AppError)
async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
	return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
	logger.exception("Error de base de datos", exc_info=exc)
	return JSONResponse(status_code=500, content={"detail": "Error interno de base de datos"})


@app.exception_handler(Exception)
async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
	logger.exception("Error inesperado", exc_info=exc)
	return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


@app.get(f"{settings.api_prefix}/health", tags=["Sistema"])
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get(f"{settings.api_prefix}/version", tags=["Sistema"])
def version() -> dict[str, str]:
	return {"version": app.version}


for controller in (
	authentication_controller,
	usuarios_controller,
	roles_controller,
	activos_controller,
	auditoria_controller,
	sucursales_controller,
	departamentos_controller,
	marcas_controller,
	modelos_controller,
	tipos_equipo_controller,
	estados_equipo_controller,
):
	app.include_router(controller.router, prefix=settings.api_prefix)
