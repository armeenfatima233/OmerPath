"""grant authenticated document access

Revision ID: fcc18231756b
Revises: 8c62d7cbebdd
Create Date: 2026-08-23 00:58:42.762199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcc18231756b'
down_revision: Union[str, Sequence[str], None] = '8c62d7cbebdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT, INSERT, DELETE
        ON TABLE public.documents
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE SELECT, INSERT, DELETE
        ON TABLE public.documents
        FROM authenticated;
        """
    )
