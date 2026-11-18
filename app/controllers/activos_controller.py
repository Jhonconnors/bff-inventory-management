"""Endpoints de inventario y ciclo de vida de activos."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_authenticated, require_roles
from app.database import get_db
from app.models.entities import Usuario
from app.repositories.activo_repository import ActivoRepository
from app.schemas.entities import ActivoCreate, ActivoRead, ActivoUpdate, AsignacionRequest, AuditoriaRead, BajaRequest, TrasladoRequest
from app.services.activo_service import ActivoService

router = APIRouter(prefix="/activos", tags=["Activos"])
READ = require_authenticated
WRITE = require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO")


@router.get("", response_model=list[ActivoRead])
def list_assets(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user: Usuario = Depends(READ)):
    return ActivoService(ActivoRepository(session)).list(limit, offset)[0]


@router.get("/busqueda", response_model=list[ActivoRead])
def search_assets(placa: str | None = None, serie: str | None = None, id_usuario: int | None = Query(None, gt=0), id_departamento: int | None = Query(None, gt=0), id_sucursal: int | None = Query(None, gt=0), id_estado: int | None = Query(None, gt=0), id_tipo: int | None = Query(None, gt=0), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user: Usuario = Depends(READ)):
    filters = {key: value for key, value in {"placa": placa, "serie": serie, "id_usuario": id_usuario, "id_departamento": id_departamento, "id_sucursal": id_sucursal, "id_estado": id_estado, "id_tipo": id_tipo}.items() if value is not None}
    return ActivoService(ActivoRepository(session)).search(filters, limit, offset)[0]


@router.post("", response_model=ActivoRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: ActivoCreate, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).create(payload.model_dump(), user.id_usuario)


@router.get("/{id_activo}", response_model=ActivoRead)
def get_asset(id_activo: int, session: Session = Depends(get_db), _user: Usuario = Depends(READ)):
    return ActivoService(ActivoRepository(session)).get(id_activo)


@router.put("/{id_activo}", response_model=ActivoRead)
def update_asset(id_activo: int, payload: ActivoUpdate, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).update(id_activo, payload.model_dump(), user.id_usuario)


@router.get("/{id_activo}/historial", response_model=list[AuditoriaRead])
def asset_history(id_activo: int, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user: Usuario = Depends(READ)):
    return ActivoService(ActivoRepository(session)).history(id_activo, limit, offset)[0]


@router.post("/{id_activo}/asignar", response_model=ActivoRead)
def assign_asset(id_activo: int, payload: AsignacionRequest, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).assign(id_activo, payload.id_usuario, payload.id_sucursal, payload.id_departamento, payload.nota_interna, user.id_usuario)


@router.post("/{id_activo}/trasladar", response_model=ActivoRead)
def transfer_asset(id_activo: int, payload: TrasladoRequest, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).transfer(id_activo, payload.id_usuario, payload.id_sucursal, payload.id_departamento, payload.nota_interna, user.id_usuario)


@router.post("/{id_activo}/devolver", response_model=ActivoRead)
def return_asset(id_activo: int, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).return_asset(id_activo, user.id_usuario)


@router.post("/{id_activo}/baja", response_model=ActivoRead)
def deactivate_asset(id_activo: int, payload: BajaRequest, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    return ActivoService(ActivoRepository(session)).deactivate(id_activo, user.id_usuario, payload.resolucion, payload.fecha, payload.motivo)


@router.delete("/{id_activo}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(id_activo: int, session: Session = Depends(get_db), user: Usuario = Depends(WRITE)):
    ActivoService(ActivoRepository(session)).deactivate(id_activo, user.id_usuario, "Baja lógica por endpoint DELETE", datetime.now().astimezone(), "Solicitud de eliminación lógica", action="DELETE")
    return Response(status_code=status.HTTP_204_NO_CONTENT)