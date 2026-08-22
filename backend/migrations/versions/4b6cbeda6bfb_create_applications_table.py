"""create applications table

Revision ID: 4b6cbeda6bfb
Revises: afa58f2c9e34
Create Date: 2026-08-22 23:39:24.231973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6cbeda6bfb'
down_revision: Union[str, Sequence[str], None] = 'afa58f2c9e34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('scholarship_id', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='Preparing', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('next_action', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['scholarship_id'], ['scholarships.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'scholarship_id', name='uq_applications_user_scholarship'),
    )
    op.create_index(
        'ix_applications_scholarship_id',
        'applications',
        ['scholarship_id'],
    )
    op.execute("ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_applications_scholarship_id', table_name='applications')
    op.drop_table('applications')
