"""create user settings table

Revision ID: 0b2cb914b372
Revises: e058407b474c
Create Date: 2026-08-23 01:20:52.765943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2cb914b372'
down_revision: Union[str, Sequence[str], None] = 'e058407b474c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_settings',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('deadline_reminders', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('eligibility_changes', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('advisor_nudges', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('weekly_digest', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('share_analytics', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('user_id'),
    )
    op.execute("ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_settings')
