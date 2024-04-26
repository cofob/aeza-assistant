"""Add is_admin and priority

Revision ID: 4b1c2bcb9ba9
Revises: b02a40ae71f9
Create Date: 2024-04-26 20:54:29.869301+00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "4b1c2bcb9ba9"
down_revision = "b02a40ae71f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "chats",
        sa.Column(
            "priority", sa.SmallInteger(), nullable=False, server_default=sa.text("0")
        ),
    )
    op.alter_column(
        "chats", "is_subscribed", existing_type=sa.BOOLEAN(), nullable=False
    )


def downgrade() -> None:
    op.alter_column("chats", "is_subscribed", existing_type=sa.BOOLEAN(), nullable=True)
    op.drop_column("chats", "priority")
    op.drop_column("chats", "is_admin")
