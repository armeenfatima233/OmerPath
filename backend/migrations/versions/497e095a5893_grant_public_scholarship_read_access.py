"""grant public scholarship read access

Revision ID: 497e095a5893
Revises: 4181bd34d657
Create Date: 2026-08-22 22:50:00.479577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '497e095a5893'
down_revision: Union[str, Sequence[str], None] = '4181bd34d657'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT
        ON TABLE public.scholarships
        TO anon;
        """
    )

    op.execute(
        """
        GRANT SELECT
        ON TABLE public.scholarships
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE SELECT
        ON TABLE public.scholarships
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE SELECT
        ON TABLE public.scholarships
        FROM anon;
        """
    )
