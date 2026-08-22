"""grant authenticated notification access

Revision ID: e058407b474c
Revises: 281abdf2b644
Create Date: 2026-08-23 01:20:51.654684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e058407b474c'
down_revision: Union[str, Sequence[str], None] = '281abdf2b644'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT
        ON TABLE public.notifications
        TO authenticated;
        """
    )

    op.execute(
        """
        GRANT UPDATE (is_read)
        ON TABLE public.notifications
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE UPDATE (is_read)
        ON TABLE public.notifications
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE SELECT
        ON TABLE public.notifications
        FROM authenticated;
        """
    )
