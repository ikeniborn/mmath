"""Store the proposal confidence beside the proposed action for offline calibration.

Revision ID: 0007_policy_confidence
Revises: 0006_policy_audit
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_policy_confidence"
down_revision = "0006_policy_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("policy_decisions", sa.Column("confidence", sa.Float))


def downgrade():
    op.drop_column("policy_decisions", "confidence")
