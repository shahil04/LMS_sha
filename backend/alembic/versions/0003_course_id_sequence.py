"""Add sequential course IDs."""

from alembic import op
import sqlalchemy as sa


revision = "0003_course_id_sequence"
down_revision = "0002_profile_password"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_id_sequences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("next_value", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "course_id_sequences",
            sa.column("id", sa.Integer()),
            sa.column("next_value", sa.Integer()),
        ),
        [{"id": 1, "next_value": 0}],
    )


def downgrade() -> None:
    op.drop_table("course_id_sequences")
