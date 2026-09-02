from alembic import op
import sqlalchemy as sa


revision = "a7b8c9d0e1f2"

down_revision = "f77e9babb66d"

branch_labels = None

depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidates",
        sa.Column(
            "embedding",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "candidates",
        "embedding",
    )