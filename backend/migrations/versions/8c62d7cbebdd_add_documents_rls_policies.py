"""add documents rls policies

Revision ID: 8c62d7cbebdd
Revises: ecb4d5b2c4f9
Create Date: 2026-08-23 00:58:41.603639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c62d7cbebdd'
down_revision: Union[str, Sequence[str], None] = 'ecb4d5b2c4f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create policy documents_select_own
        on public.documents
        for select
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy documents_insert_own
        on public.documents
        for insert
        to authenticated
        with check ((select auth.uid()) = user_id);
        """
    )

    op.execute(
        """
        create policy documents_delete_own
        on public.documents
        for delete
        to authenticated
        using ((select auth.uid()) = user_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop policy if exists documents_delete_own on public.documents;")
    op.execute("drop policy if exists documents_insert_own on public.documents;")
    op.execute("drop policy if exists documents_select_own on public.documents;")
