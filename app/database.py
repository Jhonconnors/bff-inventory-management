"""Configuración SQLAlchemy y dependencia de sesión para FastAPI."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
	"""Base común de los modelos ORM."""


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
	"""Entrega una sesión y garantiza su cierre al terminar la request."""
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()
