"""add notifications rls policies

Revision ID: 281abdf2b644
Revises: a7a6686378ba
Create Date: 2026-08-23 01:20:50.537086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '281abdf2b644'
down_revision: Union[str, Sequence[str], None] = 'a7a6686378ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No insert policy: notifications are system-generated only (by the
    # backend's own privileged connection, which bypasses RLS entirely).
    # Authenticated users can read and mark-as-read their own notifications,
    # never create one directly.
    op.execute(
        """
        create policy notifications_select_own
        on public.notifications
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy notifications_update_own
        on public.notifications
        for update
        to authenticated
        using ((select auth.uid()) = user_id)
        with check ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists notifications_update_own on public.notifications;")
    op.execute("drop policy if exists notifications_select_own on public.notifications;")
