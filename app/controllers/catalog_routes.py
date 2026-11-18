"""Factoría de controllers CRUD para los catálogos simples."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_authenticated, require_roles
from app.database import get_db

READ = require_authenticated
WRITE = require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")


def build_catalog_router(path: str, tag: str, service_type, create_schema, read_schema, id_field: str) -> APIRouter:
    """Construye un router CRUD delegando todas las reglas al servicio."""
    router = APIRouter(prefix=f"/{path}", tags=[tag])

    @router.get("", response_model=list[read_schema])
    def list_items(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user=Depends(READ)):
        return service_type(session).list(limit, offset)[0]

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_item(payload: create_schema, session: Session = Depends(get_db), _user=Depends(WRITE)):
        return service_type(session).create(payload.model_dump())

    @router.get("/{entity_id}", response_model=read_schema)
    def get_item(entity_id: int, session: Session = Depends(get_db), _user=Depends(READ)):
        return service_type(session).get(entity_id)

    @router.put("/{entity_id}", response_model=read_schema)
    def update_item(entity_id: int, payload: create_schema, session: Session = Depends(get_db), _user=Depends(WRITE)):
        return service_type(session).update(entity_id, payload.model_dump())

    @router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(entity_id: int, session: Session = Depends(get_db), _user=Depends(WRITE)):
        service_type(session).delete(entity_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router