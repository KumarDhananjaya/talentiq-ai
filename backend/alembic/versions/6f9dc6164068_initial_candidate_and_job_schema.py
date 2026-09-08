"""initial candidate and job schema

Revision ID: 6f9dc6164068
Revises:
Create Date: 2026-09-01 21:46:45.202521
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f9dc6164068"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial candidate and job schema."""

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("experience_years", sa.Float(), nullable=True),
    )

    op.create_table(
        "candidate_experiences",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
        ),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Drop initial candidate and job schema."""

    op.drop_table("candidate_experiences")
    op.drop_table("jobs")
    op.drop_table("candidates")