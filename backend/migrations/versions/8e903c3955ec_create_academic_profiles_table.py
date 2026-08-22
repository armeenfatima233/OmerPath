"""create academic profiles table

Revision ID: 8e903c3955ec
Revises: 915b6654749c
Create Date: 2026-08-22 21:57:25.231355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e903c3955ec'
down_revision: Union[str, Sequence[str], None] = '915b6654749c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'academic_profiles',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('current_degree', sa.String(length=150), nullable=True),
        sa.Column('field_of_study', sa.String(length=150), nullable=True),
        sa.Column('target_degree', sa.String(length=50), nullable=True),
        sa.Column('gpa', sa.String(length=20), nullable=True),
        sa.Column('language_test_type', sa.String(length=50), nullable=True),
        sa.Column('language_test_score', sa.String(length=20), nullable=True),
        sa.Column('experience_summary', sa.String(length=255), nullable=True),
        sa.Column('preferred_destinations', sa.ARRAY(sa.String(length=100)), server_default='{}', nullable=False),
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('user_id'),
    )
    op.execute("ALTER TABLE public.academic_profiles ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('academic_profiles')
