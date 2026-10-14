"""Add password hashes for backend-managed authentication."""

from alembic import op
import sqlalchemy as sa


revision = "0002_profile_password"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("password_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "password_hash")
