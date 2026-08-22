"""grant authenticated user settings access

Revision ID: 32c39ebed607
Revises: d30d01036751
Create Date: 2026-08-23 01:20:55.159147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32c39ebed607'
down_revision: Union[str, Sequence[str], None] = 'd30d01036751'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT, INSERT, UPDATE
        ON TABLE public.user_settings
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE SELECT, INSERT, UPDATE
        ON TABLE public.user_settings
        FROM authenticated;
        """
    )
