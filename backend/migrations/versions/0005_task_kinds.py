"""Problem kind and prompt for the research-based task families.

Revision ID: 0005_task_kinds
Revises: 0004_skill_state
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_task_kinds"
down_revision = "0004_skill_state"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("problems", sa.Column("kind", sa.String(12), nullable=False, server_default="result"))
    op.add_column("problems", sa.Column("prompt", sa.JSON))


def downgrade():
    op.drop_column("problems", "prompt")
    op.drop_column("problems", "kind")
