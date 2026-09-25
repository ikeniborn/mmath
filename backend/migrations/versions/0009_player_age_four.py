"""Accept four-year-olds: the picture mode targets ages 4-5.

Revision ID: 0009_player_age_four
Revises: 0008_skill_streaks
"""

from alembic import op

revision = "0009_player_age_four"
down_revision = "0008_skill_streaks"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("player_age_range", "players", type_="check")
    op.create_check_constraint("player_age_range", "players", "age BETWEEN 4 AND 10")


def downgrade():
    op.drop_constraint("player_age_range", "players", type_="check")
    op.create_check_constraint("player_age_range", "players", "age BETWEEN 5 AND 10")
