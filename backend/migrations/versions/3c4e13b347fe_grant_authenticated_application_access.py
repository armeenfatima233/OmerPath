"""grant authenticated application access

Revision ID: 3c4e13b347fe
Revises: 896f206e505b
Create Date: 2026-08-22 23:39:26.498124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4e13b347fe'
down_revision: Union[str, Sequence[str], None] = '896f206e505b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT, INSERT
        ON TABLE public.applications
        TO authenticated;
        """
    )

    op.execute(
        """
        GRANT UPDATE (
            status,
            progress,
            next_action
        )
        ON TABLE public.applications
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE UPDATE (
            status,
            progress,
            next_action
        )
        ON TABLE public.applications
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE SELECT, INSERT
        ON TABLE public.applications
        FROM authenticated;
        """
    )
