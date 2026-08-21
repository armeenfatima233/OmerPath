"""link profiles to auth users

Revision ID: 554b38ab838c
Revises: e6df1fd60011
Create Date: 2026-08-16 02:18:02.028943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '554b38ab838c'
down_revision: Union[str, Sequence[str], None] = 'e6df1fd60011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "profiles_id_fkey",
        "profiles",
        "users",
        ["id"],
        ["id"],
        source_schema="public",
        referent_schema="auth",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "profiles_id_fkey",
        "profiles",
        schema="public",
        type_="foreignkey",
    )
