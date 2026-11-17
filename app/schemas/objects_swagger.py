from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# =========================
# AUTHENTICATIONS
# =========================

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# ROLES
# =========================

class Rol(BaseModel):
    id_rol: Optional[int] = None
    nombre: str


# =========================
# USUARIOS
# =========================

class Usuario(BaseModel):
    id_usuario: Optional[int] = None
    nombre: str
    correo: EmailStr
    activo: bool = True
    id_rol: int


class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    id_rol: int


# =========================
# CATALOGOS
# =========================

class Sucursal(BaseModel):
    id_sucursal: Optional[int] = None
    nombre: str


class Departamento(BaseModel):
    id_departamento: Optional[int] = None
    nombre: str


class Marca(BaseModel):
    id_marca: Optional[int] = None
    nombre: str


class Modelo(BaseModel):
    id_modelo: Optional[int] = None
    nombre: str
    id_marca: int


class TipoEquipo(BaseModel):
    id_tipo: Optional[int] = None
    nombre: str


class EstadoEquipo(BaseModel):
    id_estado: Optional[int] = None
    nombre: str


# =========================
# ACTIVOS
# =========================

class Activo(BaseModel):
    id_activo: Optional[int] = None
    placa: str
    serie: str
    mac: Optional[str] = None
    posicion_monitor: Optional[str] = None
    fecha_registro: Optional[datetime] = None

    id_tipo: int
    id_marca: int
    id_modelo: int
    id_estado: int
    id_sucursal: int
    id_departamento: int
    id_usuario: Optional[int] = None


class ActivoCreate(BaseModel):
    placa: str
    serie: str
    mac: Optional[str] = None
    posicion_monitor: Optional[str] = None

    id_tipo: int
    id_marca: int
    id_modelo: int
    id_estado: int
    id_sucursal: int
    id_departamento: int
    id_usuario: Optional[int] = None


class ActivoUpdate(ActivoCreate):
    pass


# =========================
# AUDITORIA
# =========================

class Auditoria(BaseModel):
    id_evento: Optional[int] = None
    accion: str
    detalle: str
    fecha_hora: datetime
    id_activo: int
    id_usuario: int


# =========================
# DASHBOARD
# =========================

class DashboardResumen(BaseModel):
    total_activos: int
    total_usuarios: int
    total_sucursales: int


# =========================
# SISTEMA
# =========================

class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    version: str