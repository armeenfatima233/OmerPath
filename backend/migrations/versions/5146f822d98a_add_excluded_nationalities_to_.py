"""add excluded nationalities to scholarships

Revision ID: 5146f822d98a
Revises: 3c4e13b347fe
Create Date: 2026-08-23 00:29:49.349023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5146f822d98a'
down_revision: Union[str, Sequence[str], None] = '3c4e13b347fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'scholarships',
        sa.Column('excluded_nationalities', sa.ARRAY(sa.String(length=100)), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scholarships', 'excluded_nationalities')
