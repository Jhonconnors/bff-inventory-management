"""Modelos ORM correspondientes al esquema físico SIGATI+."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rol(Base):
    """Rol asignable a usuarios."""

    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    """Cuenta del sistema; la baja se representa mediante `activo`."""

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    correo: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol", ondelete="RESTRICT"), nullable=False)
    rol: Mapped[Rol] = relationship(back_populates="usuarios")
    activos: Mapped[list["Activo"]] = relationship(back_populates="usuario")


class Sucursal(Base):
    """Sucursal organizacional."""

    __tablename__ = "sucursales"

    id_sucursal: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class Departamento(Base):
    """Departamento organizacional."""

    __tablename__ = "departamentos"

    id_departamento: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class Marca(Base):
    """Fabricante del modelo de un activo."""

    __tablename__ = "marcas"

    id_marca: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    modelos: Mapped[list["Modelo"]] = relationship(back_populates="marca")


class Modelo(Base):
    """Modelo de equipo relacionado con una marca."""

    __tablename__ = "modelos"

    id_modelo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    id_marca: Mapped[int] = mapped_column(ForeignKey("marcas.id_marca", ondelete="RESTRICT"), nullable=False)
    marca: Mapped[Marca] = relationship(back_populates="modelos")
    __table_args__ = (UniqueConstraint("nombre", "id_marca", name="uq_modelos_nombre_marca"),)


class TipoEquipo(Base):
    """Catálogo de tipos de equipo."""

    __tablename__ = "tipos_equipo"

    id_tipo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class EstadoEquipo(Base):
    """Catálogo de estados de equipo."""

    __tablename__ = "estados_equipo"

    id_estado: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class Activo(Base):
    """Activo tecnológico; mantiene placa y serie únicas en PostgreSQL."""

    __tablename__ = "activos"

    id_activo: Mapped[int] = mapped_column(Integer, primary_key=True)
    placa: Mapped[str] = mapped_column(String(80), nullable=False)
    serie: Mapped[str] = mapped_column(String(120), nullable=False)
    mac: Mapped[str | None] = mapped_column(String(17))
    posicion_monitor: Mapped[str | None] = mapped_column(String(120))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    id_tipo: Mapped[int] = mapped_column(ForeignKey("tipos_equipo.id_tipo", ondelete="RESTRICT"), nullable=False)
    id_marca: Mapped[int] = mapped_column(ForeignKey("marcas.id_marca", ondelete="RESTRICT"), nullable=False)
    id_modelo: Mapped[int] = mapped_column(ForeignKey("modelos.id_modelo", ondelete="RESTRICT"), nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estados_equipo.id_estado", ondelete="RESTRICT"), nullable=False)
    id_sucursal: Mapped[int] = mapped_column(ForeignKey("sucursales.id_sucursal", ondelete="RESTRICT"), nullable=False)
    id_departamento: Mapped[int] = mapped_column(ForeignKey("departamentos.id_departamento", ondelete="RESTRICT"), nullable=False)
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"))
    tipo: Mapped[TipoEquipo] = relationship()
    marca: Mapped[Marca] = relationship()
    modelo: Mapped[Modelo] = relationship()
    estado: Mapped[EstadoEquipo] = relationship()
    sucursal: Mapped[Sucursal] = relationship()
    departamento: Mapped[Departamento] = relationship()
    usuario: Mapped[Usuario | None] = relationship(back_populates="activos")
    eventos: Mapped[list["BitacoraAuditoria"]] = relationship(back_populates="activo", order_by="BitacoraAuditoria.fecha_hora")
    __table_args__ = (
        UniqueConstraint("placa", name="uq_activos_placa"),
        UniqueConstraint("serie", name="uq_activos_serie"),
    )


class BitacoraAuditoria(Base):
    """Registro de auditoría de solo inserción."""

    __tablename__ = "bitacora_auditoria"

    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True)
    accion: Mapped[str] = mapped_column(String(30), nullable=False)
    detalle: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    id_activo: Mapped[int] = mapped_column(ForeignKey("activos.id_activo", ondelete="RESTRICT"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"), nullable=False)
    activo: Mapped[Activo] = relationship(back_populates="eventos")
    usuario: Mapped[Usuario] = relationship()