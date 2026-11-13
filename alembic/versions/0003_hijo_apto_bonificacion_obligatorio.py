"""hijo: apto para bonificación Sí/No obligatorio (por defecto No)

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-13 01:40:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '0003'
down_revision: str | None = '0002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE hijo SET apto_bonificacion = false WHERE apto_bonificacion IS NULL")
    op.alter_column(
        'hijo',
        'apto_bonificacion',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    )


def downgrade() -> None:
    op.alter_column(
        'hijo', 'apto_bonificacion', existing_type=sa.Boolean(), nullable=True, server_default=None
    )
