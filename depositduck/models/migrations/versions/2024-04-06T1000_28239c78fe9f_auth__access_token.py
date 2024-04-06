"""auth__access_token

Revision ID: 28239c78fe9f
Revises: f23c1e57b116
Create Date: 2024-04-06 10:00:53.541575

(c) 2024 Alberto Morón Hernández
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from fastapi_users_db_sqlmodel.generics import TIMESTAMPAware

# revision identifiers, used by Alembic.
revision: str = "28239c78fe9f"
down_revision: Union[str, None] = "f23c1e57b116"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth__access_token",
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column("created_at", TIMESTAMPAware(timezone=True), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth__user.id"],
        ),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        op.f("ix_auth__access_token_created_at"),
        "auth__access_token",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_auth__access_token_created_at"), table_name="auth__access_token"
    )
    op.drop_table("auth__access_token")
