"""add applications rls policies

Revision ID: 896f206e505b
Revises: 4b6cbeda6bfb
Create Date: 2026-08-22 23:39:25.343767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '896f206e505b'
down_revision: Union[str, Sequence[str], None] = '4b6cbeda6bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy applications_select_own
        on public.applications
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy applications_insert_own
        on public.applications
        for insert
        to authenticated
        with check ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy applications_update_own
        on public.applications
        for update
        to authenticated
        using ((select auth.uid()) = user_id)
        with check ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists applications_update_own on public.applications;")
    op.execute("drop policy if exists applications_insert_own on public.applications;")
    op.execute("drop policy if exists applications_select_own on public.applications;")
