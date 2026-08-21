"""create profile signup trigger

Revision ID: b4ee8ea055f3
Revises: 554b38ab838c
Create Date: 2026-08-16 02:24:00.677429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ee8ea055f3'
down_revision: Union[str, Sequence[str], None] = '554b38ab838c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        create or replace function public.handle_new_user()
        returns trigger
        language plpgsql
        security definer
        set search_path = ''
        as $$
        begin
          insert into public.profiles (id, first_name, last_name)
          values (
            new.id,
            new.raw_user_meta_data ->> 'first_name',
            new.raw_user_meta_data ->> 'last_name'
          );
          return new;
        end;
        $$;
        """
    )

    op.execute(
        """
        create trigger on_auth_user_created
        after insert on auth.users
        for each row
        execute function public.handle_new_user();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop trigger if exists on_auth_user_created on auth.users;")
    op.execute("drop function if exists public.handle_new_user();")
