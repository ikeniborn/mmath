"""Per-skill promotion and error streaks that persist across visits and sessions.

Revision ID: 0008_skill_streaks
Revises: 0007_policy_confidence
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_skill_streaks"
down_revision = "0007_policy_confidence"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("player_skills", sa.Column("correct_streak", sa.Integer, nullable=False, server_default="0"))
    op.add_column("player_skills", sa.Column("error_streak", sa.Integer, nullable=False, server_default="0"))


def downgrade():
    op.drop_column("player_skills", "error_streak")
    op.drop_column("player_skills", "correct_streak")
