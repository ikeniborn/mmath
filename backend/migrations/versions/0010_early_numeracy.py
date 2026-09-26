"""Early numeracy: wider problem kinds and the parent-chosen round length.

Revision ID: 0010_early_numeracy
Revises: 0009_player_age_four
"""

from alembic import op
import sqlalchemy as sa

revision = "0010_early_numeracy"
down_revision = "0009_player_age_four"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("problems", "kind", type_=sa.String(20), existing_type=sa.String(12))
    op.add_column("players", sa.Column("round_tasks", sa.Integer, nullable=False, server_default="10"))
    op.create_check_constraint("player_round_tasks_allowed", "players", "round_tasks IN (6, 10)")


def downgrade():
    op.drop_constraint("player_round_tasks_allowed", "players", type_="check")
    op.drop_column("players", "round_tasks")
    op.alter_column("problems", "kind", type_=sa.String(12), existing_type=sa.String(20))
