"""create saved scholarships table

Revision ID: d3b87ec771a7
Revises: 497e095a5893
Create Date: 2026-08-22 23:15:08.611922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3b87ec771a7'
down_revision: Union[str, Sequence[str], None] = '497e095a5893'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'saved_scholarships',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('scholarship_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['scholarship_id'], ['scholarships.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('user_id', 'scholarship_id'),
    )
    # Composite PK indexes (user_id, scholarship_id) leading with user_id, which
    # serves the "list saved scholarships for a user" query. A dedicated index
    # on scholarship_id speeds up the FK's cascade-delete lookup when a
    # scholarship row is removed.
    op.create_index(
        'ix_saved_scholarships_scholarship_id',
        'saved_scholarships',
        ['scholarship_id'],
    )
    op.execute("ALTER TABLE public.saved_scholarships ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_saved_scholarships_scholarship_id', table_name='saved_scholarships')
    op.drop_table('saved_scholarships')
