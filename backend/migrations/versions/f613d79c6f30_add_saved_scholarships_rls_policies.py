"""add saved scholarships rls policies

Revision ID: f613d79c6f30
Revises: d3b87ec771a7
Create Date: 2026-08-22 23:15:09.683406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f613d79c6f30'
down_revision: Union[str, Sequence[str], None] = 'd3b87ec771a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy saved_scholarships_select_own
        on public.saved_scholarships
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy saved_scholarships_insert_own
        on public.saved_scholarships
        for insert
        to authenticated
        with check ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy saved_scholarships_delete_own
        on public.saved_scholarships
        for delete
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists saved_scholarships_delete_own on public.saved_scholarships;")
    op.execute("drop policy if exists saved_scholarships_insert_own on public.saved_scholarships;")
    op.execute("drop policy if exists saved_scholarships_select_own on public.saved_scholarships;")
