"""add scholarships rls policies

Revision ID: 4181bd34d657
Revises: 8c9cc5f66880
Create Date: 2026-08-22 22:49:59.368276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4181bd34d657'
down_revision: Union[str, Sequence[str], None] = '8c9cc5f66880'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy scholarships_select_active_anon
        on public.scholarships
        for select
        to anon
        using (status = 'active');
        """
    )

    op.execute(
        """
        create policy scholarships_select_active_authenticated
        on public.scholarships
        for select
        to authenticated
        using (status = 'active');
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists scholarships_select_active_authenticated on public.scholarships;")
    op.execute("drop policy if exists scholarships_select_active_anon on public.scholarships;")
