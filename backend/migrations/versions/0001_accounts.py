"""Accounts and child profiles.

Revision ID: 0001_accounts
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_accounts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("accounts", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(320), nullable=False, unique=True), sa.Column("password_hash", sa.String(256), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("auth_sessions", sa.Column("token_hash", sa.String(64), primary_key=True), sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False), sa.Column("csrf_hash", sa.String(64), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("confirmed_at", sa.DateTime(timezone=True)), sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_index("ix_auth_sessions_account_id", "auth_sessions", ["account_id"])
    op.create_table("login_failures", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("ip_address", sa.String(64), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_login_failures_key_time", "login_failures", ["email", "ip_address", "occurred_at"])
    op.create_table("players", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.Column("age", sa.Integer, nullable=False), sa.Column("avatar", sa.String(20), nullable=False), sa.Column("topics", sa.JSON, nullable=False), sa.Column("mode", sa.String(10), nullable=False), sa.Column("difficulty_band", sa.Integer, nullable=False), sa.Column("session_minutes", sa.Integer, nullable=False), sa.CheckConstraint("age BETWEEN 5 AND 10", name="player_age_range"), sa.CheckConstraint("difficulty_band BETWEEN 0 AND 4", name="player_band_range"), sa.CheckConstraint("mode IN ('automatic', 'fixed')", name="player_mode_allowed"), sa.CheckConstraint("session_minutes IN (5, 10, 15)", name="player_minutes_allowed"))
    op.create_index("ix_players_account_id", "players", ["account_id"])


def downgrade():
    op.drop_table("players")
    op.drop_table("login_failures")
    op.drop_table("auth_sessions")
    op.drop_table("accounts")
