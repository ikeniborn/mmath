"""Hint exposure per problem and accumulated active time per session.

Revision ID: 0003_hints_timing
Revises: 0002_game_state
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_hints_timing"
down_revision = "0002_game_state"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("problems", sa.Column("hinted_at", sa.DateTime(timezone=True)))
    op.add_column("learning_sessions", sa.Column("active_ms", sa.Integer, nullable=False, server_default="0"))


def downgrade():
    op.drop_column("learning_sessions", "active_ms")
    op.drop_column("problems", "hinted_at")
