"""change candidate skills to json

Revision ID: f77e9babb66d
Revises: 6f9dc6164068
Create Date: 2026-09-02 16:27:39.667374

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f77e9babb66d"
down_revision: Union[str, Sequence[str], None] = "6f9dc6164068"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "candidates",
        "skills",
        existing_type=sa.Text(),
        type_=sa.JSON(),
        postgresql_using="""
            CASE
                WHEN skills IS NULL OR skills = ''
                    THEN '[]'::json
                ELSE json_build_array(skills)
            END
        """,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "candidates",
        "skills",
        existing_type=sa.JSON(),
        type_=sa.Text(),
        postgresql_using="skills::text",
        existing_nullable=True,
    )