"""Add Chat.forum_thread_id

Revision ID: 14818df7f851
Revises: 4b1c2bcb9ba9
Create Date: 2024-10-01 14:17:38.640592+00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "14818df7f851"
down_revision = "4b1c2bcb9ba9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("forum_thread_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("chats", "forum_thread_id")
