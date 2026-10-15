"""add mod category table

Revision ID: fe752602af6b
Revises: 33daa3820440
Create Date: 2026-10-14 09:54:09.747376
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe752602af6b"
down_revision = "33daa3820440"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mod_category",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("icon", sa.String(length=255), nullable=True),
    )

    op.bulk_insert(
        sa.table(
            "mod_category",
            sa.column("id", sa.Integer()),
            sa.column("name", sa.String(length=255)),
            sa.column("icon", sa.String(length=255)),
        ),
        [{"id": 1, "name": "Mod", "icon": "mod"}],
    )

    op.add_column(
        "mod",
        sa.Column("category", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )

    op.create_foreign_key(
        "fk_mod_category_category_mod_category",
        "mod",
        "mod_category",
        ["category"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_mod_category_category_mod_category",
        "mod",
        type_="foreignkey",
    )
    op.drop_column("mod", "category")
    op.drop_table("mod_category")