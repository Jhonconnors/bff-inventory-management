"""Endpoints de consulta exclusivamente de la bitácora."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database import get_db
from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.entities import AuditoriaRead
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])
READ = require_roles("ADMINISTRADOR", "ENCARGADO_INVENTARIO", "MESA_SERVICIOS", "CONSULTA")


@router.get("", response_model=list[AuditoriaRead])
def list_events(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), session: Session = Depends(get_db), _user=Depends(READ)):
    return AuditoriaService(AuditoriaRepository(session)).list(limit, offset)[0]


@router.get("/{id_evento}", response_model=AuditoriaRead)
def get_event(id_evento: int, session: Session = Depends(get_db), _user=Depends(READ)):
    return AuditoriaService(AuditoriaRepository(session)).get(id_evento)