"""Learning sessions, problems, attempts, policy decisions and skill aggregates.

Revision ID: 0002_game_state
Revises: 0001_accounts
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_game_state"
down_revision = "0001_accounts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "learning_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("state", sa.String(10), nullable=False),
        sa.Column("phase", sa.String(10), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("settings", sa.JSON, nullable=False),
        sa.Column("current_problem_id", postgresql.UUID(as_uuid=True)),
        sa.Column("pending_problem_id", postgresql.UUID(as_uuid=True)),
        sa.Column("last_attempt_id", postgresql.UUID(as_uuid=True)),
        sa.Column("feedback", sa.JSON),
        sa.Column("answered_count", sa.Integer, nullable=False),
        sa.Column("correct_count", sa.Integer, nullable=False),
        sa.Column("active_from", sa.DateTime(timezone=True)),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("state IN ('active', 'finished')", name="session_state_allowed"),
        sa.CheckConstraint("phase IN ('answer', 'feedback')", name="session_phase_allowed"),
    )
    op.create_index("ix_learning_sessions_player_id", "learning_sessions", ["player_id"])
    op.create_index("ux_learning_sessions_one_active", "learning_sessions", ["player_id"], unique=True, postgresql_where=sa.text("state = 'active'"))
    op.create_table(
        "problems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ordinal", sa.Integer, nullable=False),
        sa.Column("skill", sa.String(20), nullable=False),
        sa.Column("band", sa.Integer, nullable=False),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("operand_a", sa.Integer, nullable=False),
        sa.Column("operand_b", sa.Integer, nullable=False),
        sa.Column("correct_answer", sa.Integer, nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("session_id", "ordinal", name="ux_problems_session_ordinal"),
    )
    op.create_index("ix_problems_session_id", "problems", ["session_id"])
    op.create_table(
        "attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("answer", sa.Integer, nullable=False),
        sa.Column("correct", sa.Boolean, nullable=False),
        sa.Column("response_ms", sa.Integer),
        sa.Column("hint_used", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("session_id", "problem_id", name="ux_attempts_session_problem"),
    )
    op.create_index("ix_attempts_session_id", "attempts", ["session_id"])
    op.create_table(
        "policy_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("attempt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.String(10), nullable=False),
        sa.Column("allowed_actions", sa.JSON, nullable=False),
        sa.Column("state", sa.JSON, nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False),
        sa.Column("proposed_action", sa.String(20), nullable=False),
        sa.Column("applied_action", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=False),
        sa.Column("fallback_reason", sa.String(40)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_policy_decisions_session_id", "policy_decisions", ["session_id"])
    op.create_table(
        "player_skills",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill", sa.String(20), primary_key=True),
        sa.Column("band", sa.Integer, nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False),
        sa.Column("correct", sa.Integer, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("player_skills")
    op.drop_table("policy_decisions")
    op.drop_table("attempts")
    op.drop_table("problems")
    op.drop_table("learning_sessions")
