"""enable profiles rls

Revision ID: de0c9c26b022
Revises: 32c39ebed607
Create Date: 2026-08-23 06:23:36.429228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de0c9c26b022'
down_revision: Union[str, Sequence[str], None] = '32c39ebed607'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE public.profiles DISABLE ROW LEVEL SECURITY;")
