"""add per game categories

Revision ID: 9eb6f3fea778
Revises: fe752602af6b
Create Date: 2026-10-14 13:22:09.734910
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9eb6f3fea778"
down_revision = "fe752602af6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game_mod_category",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "notify",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_id"], ["mod_category.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("game_id", "category_id", name="uq_game_mod_category"),
    )


def downgrade() -> None:
    op.drop_table("game_mod_category")