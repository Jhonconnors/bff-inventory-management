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
    roles = sa.table("rol", sa.column("id_rol", sa.Integer), sa.column("nombre", sa.String(length=50)))
    connection = op.get_bind()
    for name in ("ADMINISTRADOR", "ENCARGADO_INVENTARIO", "CONSULTA"):
        exists = connection.execute(sa.select(roles.c.id_rol).where(roles.c.nombre == name)).first()
        if exists is None:
            connection.execute(sa.insert(roles).values(nombre=name))


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())