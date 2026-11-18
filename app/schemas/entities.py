"""Contratos Pydantic v2 de entrada y salida."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    """Configuración compartida para serializar entidades ORM."""

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=8, max_length=255)


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RolCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)


class RolRead(ORMModel):
    id_rol: int
    nombre: str


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    correo: EmailStr = Field(max_length=100)
    password: str = Field(min_length=12, max_length=255)
    id_rol: int = Field(gt=0)


class UsuarioUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    correo: EmailStr = Field(max_length=100)
    password: str | None = Field(default=None, min_length=12, max_length=255)
    id_rol: int = Field(gt=0)
    activo: bool = True


class UsuarioRead(ORMModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    activo: bool
    id_rol: int


class AuthenticatedUserRead(UsuarioRead):
    rol: RolRead


class CatalogCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


class CatalogRead(ORMModel):
    nombre: str


class SucursalRead(CatalogRead):
    id_sucursal: int


class DepartamentoRead(CatalogRead):
    id_departamento: int


class MarcaRead(CatalogRead):
    id_marca: int


class TipoEquipoRead(CatalogRead):
    id_tipo: int


class EstadoEquipoRead(CatalogRead):
    id_estado: int


class ModeloCreate(CatalogCreate):
    id_marca: int = Field(gt=0)


class ModeloRead(CatalogRead):
    id_modelo: int
    id_marca: int


class ActivoFields(BaseModel):
    placa: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
    serie: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
    mac: str | None = Field(default=None, max_length=50)
    posicion_monitor: str | None = Field(default=None, max_length=50)
    id_tipo: int = Field(gt=0)
    id_marca: int = Field(gt=0)
    id_modelo: int = Field(gt=0)
    id_estado: int = Field(gt=0)
    id_sucursal: int = Field(gt=0)
    id_departamento: int = Field(gt=0)
    id_usuario: int | None = Field(default=None, gt=0)


class ActivoCreate(ActivoFields):
    pass


class ActivoUpdate(ActivoFields):
    pass


class ActivoRead(ORMModel, ActivoFields):
    id_activo: int
    fecha_registro: datetime


class AsignacionRequest(BaseModel):
    id_usuario: int = Field(gt=0)
    id_sucursal: int = Field(gt=0)
    id_departamento: int = Field(gt=0)
    nota_interna: str = Field(min_length=1, max_length=2000)


class TrasladoRequest(BaseModel):
    id_usuario: int = Field(gt=0)
    id_sucursal: int = Field(gt=0)
    id_departamento: int = Field(gt=0)
    nota_interna: str | None = Field(default=None, max_length=2000)


class BajaRequest(BaseModel):
    resolucion: str = Field(min_length=1, max_length=200)
    fecha: datetime
    motivo: str = Field(min_length=1, max_length=2000)


class AuditoriaRead(ORMModel):
    id_evento: int
    accion: str
    detalle: str
    fecha_hora: datetime
    id_activo: int
    id_usuario: int


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int