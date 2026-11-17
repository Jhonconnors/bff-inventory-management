"""Endpoints de administración de usuarios."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models.entities import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.entities import UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
ADMIN = require_roles("ADMINISTRADOR")
READ_ROLES = require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO", "MESA_SERVICIOS", "CONSULTA")


@router.get("", response_model=list[UsuarioRead])
def list_users(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user: Usuario = Depends(READ_ROLES)):
    return UsuarioService(UsuarioRepository(session)).list(limit, offset)[0]


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UsuarioCreate, session: Session = Depends(get_db), _user: Usuario = Depends(ADMIN)):
    return UsuarioService(UsuarioRepository(session)).create(payload.model_dump())


@router.get("/{id_usuario}", response_model=UsuarioRead)
def get_user(id_usuario: int, session: Session = Depends(get_db), _user: Usuario = Depends(READ_ROLES)):
    return UsuarioService(UsuarioRepository(session)).get(id_usuario)


@router.put("/{id_usuario}", response_model=UsuarioRead)
def update_user(id_usuario: int, payload: UsuarioUpdate, session: Session = Depends(get_db), _user: Usuario = Depends(ADMIN)):
    return UsuarioService(UsuarioRepository(session)).update(id_usuario, payload.model_dump(exclude_unset=True))


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id_usuario: int, session: Session = Depends(get_db), _user: Usuario = Depends(ADMIN)):
    UsuarioService(UsuarioRepository(session)).delete(id_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{id_usuario}/activar", response_model=UsuarioRead)
def activate_user(id_usuario: int, session: Session = Depends(get_db), _user: Usuario = Depends(ADMIN)):
    return UsuarioService(UsuarioRepository(session)).set_active(id_usuario, True)


@router.patch("/{id_usuario}/desactivar", response_model=UsuarioRead)
def deactivate_user(id_usuario: int, session: Session = Depends(get_db), _user: Usuario = Depends(ADMIN)):
    return UsuarioService(UsuarioRepository(session)).set_active(id_usuario, False)