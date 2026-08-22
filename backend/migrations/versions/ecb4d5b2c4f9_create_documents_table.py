"""create documents table

Revision ID: ecb4d5b2c4f9
Revises: 5146f822d98a
Create Date: 2026-08-23 00:58:40.501359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecb4d5b2c4f9'
down_revision: Union[str, Sequence[str], None] = '5146f822d98a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('document_type', sa.String(length=50), server_default='Other', nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=150), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('storage_path'),
    )
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])
    op.execute("ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_documents_user_id', table_name='documents')
    op.drop_table('documents')
