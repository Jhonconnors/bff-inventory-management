"""Endpoints CRUD para roles."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database import get_db
from app.schemas.entities import RolCreate, RolRead
from app.services.rol_service import RolService

router = APIRouter(prefix="/roles", tags=["Roles"])
ADMIN = require_roles("ADMINISTRADOR")
READ = require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")


@router.get("", response_model=list[RolRead])
def list_roles(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user=Depends(READ)):
    return RolService(session).list(limit, offset)[0]


@router.post("", response_model=RolRead, status_code=status.HTTP_201_CREATED)
def create_role(payload: RolCreate, session: Session = Depends(get_db), _user=Depends(ADMIN)):
    return RolService(session).create(payload.model_dump())


@router.get("/{id_rol}", response_model=RolRead)
def get_role(id_rol: int, session: Session = Depends(get_db), _user=Depends(READ)):
    return RolService(session).get(id_rol)


@router.put("/{id_rol}", response_model=RolRead)
def update_role(id_rol: int, payload: RolCreate, session: Session = Depends(get_db), _user=Depends(ADMIN)):
    return RolService(session).update(id_rol, payload.model_dump())


@router.delete("/{id_rol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(id_rol: int, session: Session = Depends(get_db), _user=Depends(ADMIN)):
    RolService(session).delete(id_rol)
    return Response(status_code=status.HTTP_204_NO_CONTENT)