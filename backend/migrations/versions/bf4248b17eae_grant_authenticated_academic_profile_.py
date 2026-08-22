"""grant authenticated academic profile access

Revision ID: bf4248b17eae
Revises: 7a003c3261da
Create Date: 2026-08-22 21:57:28.148330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf4248b17eae'
down_revision: Union[str, Sequence[str], None] = '7a003c3261da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        GRANT SELECT
        ON TABLE public.academic_profiles
        TO authenticated;
        """
    )

    op.execute(
        """
        GRANT INSERT (
            user_id,
            current_degree,
            field_of_study,
            target_degree,
            gpa,
            language_test_type,
            language_test_score,
            experience_summary,
            preferred_destinations,
            onboarding_completed_at
        )
        ON TABLE public.academic_profiles
        TO authenticated;
        """
    )

    op.execute(
        """
        GRANT UPDATE (
            current_degree,
            field_of_study,
            target_degree,
            gpa,
            language_test_type,
            language_test_score,
            experience_summary,
            preferred_destinations,
            onboarding_completed_at
        )
        ON TABLE public.academic_profiles
        TO authenticated;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        REVOKE UPDATE (
            current_degree,
            field_of_study,
            target_degree,
            gpa,
            language_test_type,
            language_test_score,
            experience_summary,
            preferred_destinations,
            onboarding_completed_at
        )
        ON TABLE public.academic_profiles
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE INSERT (
            user_id,
            current_degree,
            field_of_study,
            target_degree,
            gpa,
            language_test_type,
            language_test_score,
            experience_summary,
            preferred_destinations,
            onboarding_completed_at
        )
        ON TABLE public.academic_profiles
        FROM authenticated;
        """
    )

    op.execute(
        """
        REVOKE SELECT
        ON TABLE public.academic_profiles
        FROM authenticated;
        """
    )
