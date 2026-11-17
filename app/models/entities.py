"""Modelos ORM correspondientes al esquema físico SIGATI+."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rol(Base):
    """Rol asignable a usuarios."""

    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    """Cuenta del sistema; la baja se representa mediante `activo`."""

    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    correo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool | None] = mapped_column(Boolean, default=True, server_default="true")
    id_rol: Mapped[int] = mapped_column(ForeignKey("rol.id_rol"), nullable=False)
    rol: Mapped[Rol] = relationship(back_populates="usuarios")
    activos: Mapped[list["Activo"]] = relationship(back_populates="usuario")


class Sucursal(Base):
    """Sucursal organizacional."""

    __tablename__ = "sucursal"

    id_sucursal: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Departamento(Base):
    """Departamento organizacional."""

    __tablename__ = "departamento"

    id_departamento: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Marca(Base):
    """Fabricante del modelo de un activo."""

    __tablename__ = "marca"

    id_marca: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    modelos: Mapped[list["Modelo"]] = relationship(back_populates="marca")


class Modelo(Base):
    """Modelo de equipo relacionado con una marca."""

    __tablename__ = "modelo"

    id_modelo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    id_marca: Mapped[int] = mapped_column(ForeignKey("marca.id_marca"), nullable=False)
    marca: Mapped[Marca] = relationship(back_populates="modelos")


class TipoEquipo(Base):
    """Catálogo de tipos de equipo."""

    __tablename__ = "tipo_equipo"

    id_tipo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class EstadoEquipo(Base):
    """Catálogo de estados de equipo."""

    __tablename__ = "estado_equipo"

    id_estado: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Activo(Base):
    """Activo tecnológico; mantiene placa y serie únicas en PostgreSQL."""

    __tablename__ = "activo"

    id_activo: Mapped[int] = mapped_column(Integer, primary_key=True)
    placa: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    serie: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    mac: Mapped[str | None] = mapped_column(String(50))
    posicion_monitor: Mapped[str | None] = mapped_column(String(50))
    fecha_registro: Mapped[datetime | None] = mapped_column(DateTime(), server_default=func.current_timestamp())
    id_tipo: Mapped[int] = mapped_column(ForeignKey("tipo_equipo.id_tipo"), nullable=False)
    id_marca: Mapped[int] = mapped_column(ForeignKey("marca.id_marca"), nullable=False)
    id_modelo: Mapped[int] = mapped_column(ForeignKey("modelo.id_modelo"), nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estado_equipo.id_estado"), nullable=False)
    id_sucursal: Mapped[int] = mapped_column(ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_departamento: Mapped[int] = mapped_column(ForeignKey("departamento.id_departamento"), nullable=False)
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuario.id_usuario"))
    tipo: Mapped[TipoEquipo] = relationship()
    marca: Mapped[Marca] = relationship()
    modelo: Mapped[Modelo] = relationship()
    estado: Mapped[EstadoEquipo] = relationship()
    sucursal: Mapped[Sucursal] = relationship()
    departamento: Mapped[Departamento] = relationship()
    usuario: Mapped[Usuario | None] = relationship(back_populates="activos")
    eventos: Mapped[list["BitacoraAuditoria"]] = relationship(back_populates="activo", order_by="BitacoraAuditoria.fecha_hora")
    __table_args__ = (
        Index("idx_activo_serie", "serie"),
        Index("idx_activo_placa", "placa"),
    )


class BitacoraAuditoria(Base):
    """Registro de auditoría de solo inserción."""

    __tablename__ = "bitacora_auditoria"

    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    detalle: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_hora: Mapped[datetime | None] = mapped_column(DateTime(), server_default=func.current_timestamp())
    id_activo: Mapped[int] = mapped_column(ForeignKey("activo.id_activo"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    activo: Mapped[Activo] = relationship(back_populates="eventos")
    usuario: Mapped[Usuario] = relationship()
    __table_args__ = (Index("idx_bitacora_activo", "id_activo"),)