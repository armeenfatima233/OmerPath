"""create scholarships table

Revision ID: 8c9cc5f66880
Revises: bf4248b17eae
Create Date: 2026-08-22 22:49:58.306957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c9cc5f66880'
down_revision: Union[str, Sequence[str], None] = 'bf4248b17eae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'scholarships',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('provider_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('funding_type', sa.String(length=30), nullable=True),
        sa.Column('coverage', sa.ARRAY(sa.String(length=150)), server_default='{}', nullable=False),
        sa.Column('degree_levels', sa.ARRAY(sa.String(length=50)), server_default='{}', nullable=False),
        sa.Column('fields_of_study', sa.ARRAY(sa.String(length=100)), server_default='{}', nullable=False),
        sa.Column('destinations', sa.ARRAY(sa.String(length=100)), server_default='{}', nullable=False),
        sa.Column('eligible_nationalities', sa.ARRAY(sa.String(length=100)), nullable=True),
        sa.Column('eligible_residences', sa.ARRAY(sa.String(length=100)), nullable=True),
        sa.Column('min_gpa', sa.String(length=20), nullable=True),
        sa.Column('language_test_type', sa.String(length=50), nullable=True),
        sa.Column('min_language_test_score', sa.String(length=20), nullable=True),
        sa.Column('min_experience', sa.String(length=255), nullable=True),
        sa.Column('age_min', sa.Integer(), nullable=True),
        sa.Column('age_max', sa.Integer(), nullable=True),
        sa.Column('eligibility_notes', sa.Text(), nullable=True),
        sa.Column('required_documents', sa.ARRAY(sa.String(length=150)), server_default='{}', nullable=False),
        sa.Column('deadline_at', sa.Date(), nullable=True),
        sa.Column('deadline_note', sa.String(length=255), nullable=True),
        sa.Column('application_opens_at', sa.Date(), nullable=True),
        sa.Column('official_source_url', sa.Text(), nullable=True),
        sa.Column('application_url', sa.Text(), nullable=True),
        sa.Column('source_label', sa.String(length=150), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        sa.Column('fit_reasons', sa.ARRAY(sa.String(length=200)), server_default='{}', nullable=False),
        sa.Column('attention_points', sa.ARRAY(sa.String(length=200)), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute("ALTER TABLE public.scholarships ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('scholarships')
