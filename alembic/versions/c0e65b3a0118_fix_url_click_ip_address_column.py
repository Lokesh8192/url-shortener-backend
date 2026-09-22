"""fix url_clicks ip_address column name

Revision ID: c0e65b3a0118
Revises: 26ea792410cf
Create Date: 2026-09-22 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c0e65b3a0118"
down_revision: Union[str, Sequence[str], None] = "26ea792410cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename legacy id_address column to ip_address if it still exists."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("url_clicks")]

    if "id_address" in columns and "ip_address" not in columns:
        with op.batch_alter_table("url_clicks") as batch_op:
            batch_op.alter_column("id_address", new_column_name="ip_address")


def downgrade() -> None:
    """Rename ip_address back to id_address."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("url_clicks")]

    if "ip_address" in columns and "id_address" not in columns:
        with op.batch_alter_table("url_clicks") as batch_op:
            batch_op.alter_column("ip_address", new_column_name="id_address")
