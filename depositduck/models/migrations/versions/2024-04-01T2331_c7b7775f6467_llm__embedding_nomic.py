"""llm__embedding_nomic

Revision ID: c7b7775f6467
Revises: d6e60a817251
Create Date: 2024-04-01 23:31:37.427997

(c) 2024 Alberto Morón Hernández
"""

from typing import Sequence, Union

import pgvector
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7b7775f6467"
down_revision: Union[str, None] = "d6e60a817251"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector https://github.com/pgvector/pgvector
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table(
        "llm__embedding_nomic",
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
        sa.Column("snippet_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("vector", pgvector.sqlalchemy.Vector(dim=768), nullable=False),
        sa.ForeignKeyConstraint(
            ["snippet_id"],
            ["llm__snippet.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("llm__embedding_nomic")
