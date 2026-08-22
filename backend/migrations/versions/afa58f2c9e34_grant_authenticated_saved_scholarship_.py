"""grant authenticated saved scholarship access

Revision ID: afa58f2c9e34
Revises: f613d79c6f30
Create Date: 2026-08-22 23:15:10.832772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afa58f2c9e34'
down_revision: Union[str, Sequence[str], None] = 'f613d79c6f30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT, INSERT, DELETE
        ON TABLE public.saved_scholarships
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE SELECT, INSERT, DELETE
        ON TABLE public.saved_scholarships
        FROM authenticated;
        """
    )
