"""add user settings rls policies

Revision ID: d30d01036751
Revises: 0b2cb914b372
Create Date: 2026-08-23 01:20:53.891720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd30d01036751'
down_revision: Union[str, Sequence[str], None] = '0b2cb914b372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy user_settings_select_own
        on public.user_settings
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy user_settings_insert_own
        on public.user_settings
        for insert
        to authenticated
        with check ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy user_settings_update_own
        on public.user_settings
        for update
        to authenticated
        using ((select auth.uid()) = user_id)
        with check ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists user_settings_update_own on public.user_settings;")
    op.execute("drop policy if exists user_settings_insert_own on public.user_settings;")
    op.execute("drop policy if exists user_settings_select_own on public.user_settings;")
