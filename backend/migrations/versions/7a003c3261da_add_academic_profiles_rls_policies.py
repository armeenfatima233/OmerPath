"""add academic profiles rls policies

Revision ID: 7a003c3261da
Revises: 8e903c3955ec
Create Date: 2026-08-22 21:57:26.716715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a003c3261da'
down_revision: Union[str, Sequence[str], None] = '8e903c3955ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy academic_profiles_select_own
        on public.academic_profiles
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy academic_profiles_insert_own
        on public.academic_profiles
        for insert
        to authenticated
        with check ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy academic_profiles_update_own
        on public.academic_profiles
        for update
        to authenticated
        using ((select auth.uid()) = user_id)
        with check ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists academic_profiles_update_own on public.academic_profiles;")
    op.execute("drop policy if exists academic_profiles_insert_own on public.academic_profiles;")
    op.execute("drop policy if exists academic_profiles_select_own on public.academic_profiles;")
