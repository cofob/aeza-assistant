"""Initial revision

Revision ID: b02a40ae71f9
Revises: 
Create Date: 2023-02-23 18:49:50.570215+00:00
"""
import sqlalchemy as sa
from alembic import op

revision = "b02a40ae71f9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("is_subscribed", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("telegram_id"),
    )


def downgrade() -> None:
    op.drop_table("chats")
