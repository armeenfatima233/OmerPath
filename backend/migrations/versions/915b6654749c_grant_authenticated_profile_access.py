"""grant authenticated profile access

Revision ID: 915b6654749c
Revises: 7ecd6f1b58d1
Create Date: 2026-08-16 03:57:05.964167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '915b6654749c'
down_revision: Union[str, Sequence[str], None] = '7ecd6f1b58d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT
        ON TABLE public.profiles
        TO authenticated;
        """
    )

    op.execute(
        """
        GRANT UPDATE (
            first_name,
            last_name,
            nationality,
            country_of_residence
        )
        ON TABLE public.profiles
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE UPDATE (
            first_name,
            last_name,
            nationality,
            country_of_residence
        )
        ON TABLE public.profiles
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE SELECT
        ON TABLE public.profiles
        FROM authenticated;
        """
    )
