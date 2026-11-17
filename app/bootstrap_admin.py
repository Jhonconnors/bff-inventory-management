"""Crea interactivamente el primer usuario administrador."""

from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.entities import Rol, Usuario


def main() -> None:
    """Solicita datos por consola y crea el administrador inicial."""
    session = SessionLocal()
    try:
        admin_role = session.scalar(select(Rol).where(Rol.nombre == "ADMINISTRADOR"))
        if admin_role is None:
            raise RuntimeError("Aplique primero las migraciones: alembic upgrade head")
        existing_admin = session.scalar(select(Usuario.id_usuario).where(Usuario.id_rol == admin_role.id_rol, Usuario.activo.is_(True)))
        if existing_admin is not None:
            raise RuntimeError("Ya existe un administrador activo")

        name = input("Nombre del administrador: ").strip()
        raw_email = input("Correo: ").strip()
        try:
            email = str(TypeAdapter(EmailStr).validate_python(raw_email)).lower()
        except ValidationError as exc:
            raise ValueError("El correo no tiene un formato válido") from exc
        password = getpass("Contraseña (mínimo 12 caracteres): ")
        confirmation = getpass("Confirme la contraseña: ")
        if len(name) < 1 or len(name) > 160:
            raise ValueError("El nombre debe contener entre 1 y 160 caracteres")
        if len(password) < 12 or len(password) > 128:
            raise ValueError("La contraseña debe contener entre 12 y 128 caracteres")
        if password != confirmation:
            raise ValueError("Las contraseñas no coinciden")
        if session.scalar(select(Usuario.id_usuario).where(Usuario.correo == email)) is not None:
            raise ValueError("El correo ya está registrado")

        session.add(Usuario(nombre=name, correo=email, password_hash=hash_password(password), activo=True, id_rol=admin_role.id_rol))
        session.commit()
        print(f"Administrador creado: {email}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()