"""Policy audit: deployment policy mode and the rule action beside the applied action.

Revision ID: 0006_policy_audit
Revises: 0005_task_kinds
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_policy_audit"
down_revision = "0005_task_kinds"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("policy_decisions", sa.Column("policy_mode", sa.String(10), nullable=False, server_default="rules"))
    op.add_column("policy_decisions", sa.Column("rule_action", sa.String(20)))
    op.alter_column("policy_decisions", "proposed_action", existing_type=sa.String(20), nullable=True)
    op.alter_column("policy_decisions", "model_version", existing_type=sa.String(40), nullable=True)


def downgrade():
    op.alter_column("policy_decisions", "model_version", existing_type=sa.String(40), nullable=False)
    op.alter_column("policy_decisions", "proposed_action", existing_type=sa.String(20), nullable=False)
    op.drop_column("policy_decisions", "rule_action")
    op.drop_column("policy_decisions", "policy_mode")
