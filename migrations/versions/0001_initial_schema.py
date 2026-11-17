"""Esquema inicial del inventario SIGATI+."""

from alembic import op
import sqlalchemy as sa

from app.database import Base
from app.models import entities  # noqa: F401

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    roles = sa.table("roles", sa.column("nombre", sa.String(length=80)))
    op.bulk_insert(roles, [{"nombre": name} for name in ("ADMINISTRADOR", "ENCARGADO_INVENTARIO", "MESA_SERVICIOS", "CONSULTA")])


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())