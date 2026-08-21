"""add profiles rls policies

Revision ID: 7ecd6f1b58d1
Revises: b4ee8ea055f3
Create Date: 2026-08-16 03:44:05.786936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ecd6f1b58d1'
down_revision: Union[str, Sequence[str], None] = 'b4ee8ea055f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy profiles_select_own
        on public.profiles
        for select
        to authenticated
        using ((select auth.uid()) = id);
        """
    )

    op.execute(
        """
        create policy profiles_update_own
        on public.profiles
        for update
        to authenticated
        using ((select auth.uid()) = id)
        with check ((select auth.uid()) = id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists profiles_update_own on public.profiles;")
    op.execute("drop policy if exists profiles_select_own on public.profiles;")
