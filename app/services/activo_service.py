"""Reglas de negocio y transacciones del inventario de activos."""

import json
import logging
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.entities import Activo, BitacoraAuditoria, Departamento, EstadoEquipo, Marca, Modelo, Sucursal, TipoEquipo, Usuario
from app.repositories.activo_repository import ActivoRepository
from app.repositories.auditoria_repository import AuditoriaRepository

logger = logging.getLogger(__name__)
CATALOG_FIELDS = {"id_tipo": TipoEquipo, "id_marca": Marca, "id_modelo": Modelo, "id_estado": EstadoEquipo, "id_sucursal": Sucursal, "id_departamento": Departamento}


class ActivoService:
    def __init__(self, repository: ActivoRepository) -> None:
        self.repository = repository
        self.session = repository.session
        self.audit_repository = AuditoriaRepository(self.session)

    def list(self, limit: int, offset: int):
        return self.repository.list(limit, offset)

    def get(self, asset_id: int) -> Activo:
        return self.repository.get_or_raise(asset_id)

    def search(self, filters: dict, limit: int, offset: int):
        return self.repository.search(limit=limit, offset=offset, filters=filters)

    def history(self, asset_id: int, limit: int, offset: int):
        self.get(asset_id)
        return self.audit_repository.for_asset(asset_id, limit, offset)

    def create(self, values: dict, actor_id: int) -> Activo:
        self._validate_asset(values)
        self._validate_user(values.get("id_usuario"))
        self._validate_assigned_state(values["id_estado"], values.get("id_usuario"))
        self._ensure_unique(values["placa"], values["serie"])
        return self._mutate("CREATE", actor_id, lambda: self.repository.add(values), {"activo": values})

    def update(self, asset_id: int, values: dict, actor_id: int) -> Activo:
        self._validate_asset(values)
        self._validate_user(values.get("id_usuario"))
        self._validate_assigned_state(values["id_estado"], values.get("id_usuario"))
        self._ensure_unique(values["placa"], values["serie"], asset_id)
        asset = self.get(asset_id)
        previous = self._asset_snapshot(asset)
        return self._mutate("UPDATE", actor_id, lambda: self.repository.update(asset, values), {"antes": previous, "despues": values})

    def assign(self, asset_id: int, user_id: int, note: str, actor_id: int) -> Activo:
        asset = self.get(asset_id)
        self._validate_user(user_id)
        assigned_state = self._state_by_name("Asignado")
        if assigned_state is None:
            raise BusinessRuleError("Debe existir el estado 'Asignado' para asignar activos")
        before = self._asset_snapshot(asset)
        def change():
            asset.id_usuario = user_id
            asset.id_estado = assigned_state.id_estado
            self.session.flush()
            return asset
        return self._mutate("ASSIGN", actor_id, change, {"antes": before, "id_usuario": user_id, "nota_interna": note})

    def transfer(self, asset_id: int, user_id: int, branch_id: int, department_id: int, note: str | None, actor_id: int) -> Activo:
        asset = self.get(asset_id)
        self._validate_user(user_id)
        self._validate_catalog("id_sucursal", branch_id)
        self._validate_catalog("id_departamento", department_id)
        before = self._asset_snapshot(asset)
        after = {"id_usuario": user_id, "id_sucursal": branch_id, "id_departamento": department_id}
        def change():
            for key, value in after.items():
                setattr(asset, key, value)
            self.session.flush()
            return asset
        return self._mutate("TRANSFER", actor_id, change, {"antes": before, "despues": after, "nota_interna": note})

    def return_asset(self, asset_id: int, actor_id: int) -> Activo:
        asset = self.get(asset_id)
        available = self._state_by_name("Disponible en bodega")
        if available is None:
            raise BusinessRuleError("Debe existir el estado 'Disponible en bodega' para devolver activos")
        before = self._asset_snapshot(asset)
        def change():
            asset.id_estado = available.id_estado
            asset.id_usuario = None
            self.session.flush()
            return asset
        return self._mutate("RETURN", actor_id, change, {"antes": before, "id_estado": available.id_estado, "id_usuario": None})

    def deactivate(self, asset_id: int, actor_id: int, resolution: str, date: datetime, reason: str, action: str = "DEACTIVATE") -> Activo:
        asset = self.get(asset_id)
        retired = self._state_by_name("Baja")
        if retired is None:
            raise BusinessRuleError("Debe existir el estado 'Baja' para dar de baja el activo")
        before = self._asset_snapshot(asset)
        details = {"antes": before, "resolucion": resolution, "fecha": date.isoformat(), "motivo": reason}
        def change():
            asset.id_estado = retired.id_estado
            asset.id_usuario = None
            self.session.flush()
            return asset
        return self._mutate(action, actor_id, change, details)

    def _validate_asset(self, values: dict) -> None:
        required = ("placa", "serie", *CATALOG_FIELDS)
        missing = [field for field in required if values.get(field) is None or values.get(field) == ""]
        if missing:
            raise BusinessRuleError(f"Campos obligatorios faltantes: {', '.join(missing)}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", values["placa"]):
            raise BusinessRuleError("Formato de placa inválido")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", values["serie"]):
            raise BusinessRuleError("Formato de serie inválido")
        if values.get("mac") and not re.fullmatch(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", values["mac"]):
            raise BusinessRuleError("Formato de MAC inválido")
        for field in CATALOG_FIELDS:
            self._validate_catalog(field, values[field])
        model = self.session.get(Modelo, values["id_modelo"])
        if model.id_marca != values["id_marca"]:
            raise BusinessRuleError("El modelo no pertenece a la marca seleccionada")

    def _validate_catalog(self, field: str, entity_id: int) -> None:
        model = CATALOG_FIELDS[field]
        if self.session.get(model, entity_id) is None:
            raise NotFoundError(f"El catálogo {field}={entity_id} no existe")

    def _validate_user(self, user_id: int | None) -> None:
        if user_id is not None:
            user = self.session.get(Usuario, user_id)
            if user is None or not user.activo:
                raise NotFoundError(f"Usuario {user_id} no existe o está inactivo")

    def _validate_assigned_state(self, state_id: int, user_id: int | None) -> None:
        state = self.session.get(EstadoEquipo, state_id)
        if state and state.nombre.casefold() == "asignado" and user_id is None:
            raise BusinessRuleError("Un activo con estado Asignado debe tener usuario responsable")

    def _ensure_unique(self, placa: str, serie: str, exclude_id: int | None = None) -> None:
        duplicate = self.repository.duplicate(placa, serie, exclude_id)
        if duplicate:
            raise ConflictError(f"La {duplicate} ya está registrada")

    def _state_by_name(self, name: str):
        return self.session.scalar(select(EstadoEquipo).where(EstadoEquipo.nombre.ilike(name)))

    @staticmethod
    def _asset_snapshot(asset: Activo) -> dict:
        return {key: getattr(asset, key) for key in ("placa", "serie", "id_tipo", "id_marca", "id_modelo", "id_estado", "id_sucursal", "id_departamento", "id_usuario")}

    def _mutate(self, action: str, actor_id: int, mutation, details: dict) -> Activo:
        try:
            asset = mutation()
            self.session.add(BitacoraAuditoria(accion=action, detalle=json.dumps(details, ensure_ascii=False, default=str), id_activo=asset.id_activo, id_usuario=actor_id))
            self.session.commit()
            logger.info("Activo %s: evento %s", asset.id_activo, action)
            return asset
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("La operación viola una restricción de integridad") from exc
        except Exception:
            self.session.rollback()
            raise