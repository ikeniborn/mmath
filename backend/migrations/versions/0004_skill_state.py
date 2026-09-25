"""Skill windows, streaks and mastery; error types; decision outcome links; profile theme.

Revision ID: 0004_skill_state
Revises: 0003_hints_timing
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_skill_state"
down_revision = "0003_hints_timing"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("player_skills", sa.Column("recent", sa.JSON, nullable=False, server_default="[]"))
    op.add_column("learning_sessions", sa.Column("correct_streak", sa.Integer, nullable=False, server_default="0"))
    op.add_column("learning_sessions", sa.Column("error_streak", sa.Integer, nullable=False, server_default="0"))
    op.add_column("learning_sessions", sa.Column("skill_run", sa.Integer, nullable=False, server_default="0"))
    op.add_column("player_skills", sa.Column("mastery", sa.Float))
    op.add_column("player_skills", sa.Column("formula_version", sa.String(40)))
    op.add_column("attempts", sa.Column("error_type", sa.String(24)))
    op.add_column("policy_decisions", sa.Column("next_problem_id", postgresql.UUID(as_uuid=True)))
    op.add_column("players", sa.Column("theme", sa.String(20), nullable=False, server_default="flowers"))
    op.create_check_constraint("player_theme_allowed", "players", "theme IN ('flowers', 'dolls', 'cars', 'construction')")


def downgrade():
    op.drop_constraint("player_theme_allowed", "players", type_="check")
    op.drop_column("players", "theme")
    op.drop_column("policy_decisions", "next_problem_id")
    op.drop_column("attempts", "error_type")
    for column in ("skill_run", "error_streak", "correct_streak"):
        op.drop_column("learning_sessions", column)
    for column in ("formula_version", "mastery", "recent"):
        op.drop_column("player_skills", column)
