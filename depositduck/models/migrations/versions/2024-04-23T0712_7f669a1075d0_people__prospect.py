"""people__prospect

Revision ID: 7f669a1075d0
Revises: d6f3c7a542f7
Create Date: 2024-04-23 07:12:57.082754

(c) 2024 Alberto Morón Hernández
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f669a1075d0"
down_revision: Union[str, None] = "90054aafa739"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "people__prospect",
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "deposit_provider_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth__user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint("uq_email", "people__prospect", ["email"])
    op.create_index(
        op.f("ix_people__prospect_email"), "people__prospect", ["email"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_people__prospect_email"), table_name="people__prospect")
    op.drop_constraint("uq_email", "people__prospect", type_="unique")
    op.drop_table("people__prospect")
