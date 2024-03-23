"""llm__embedding_minilml6v2

Revision ID: 5c6c3dbda309
Revises: a7e319f79899
Create Date: 2024-03-23 09:10:57.092472

(c) 2024 Alberto Morón Hernández
"""

from typing import Sequence, Union

import pgvector
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c6c3dbda309"
down_revision: Union[str, None] = "a7e319f79899"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector https://github.com/pgvector/pgvector
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table(
        "llm__embedding_minilm_l6_v2",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("vector", pgvector.sqlalchemy.Vector(dim=384), nullable=False),
        sa.Column("llm_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["llm_name"],
            ["llm__llm.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("llm__embedding_minilm_l6_v2")

    op.execute(sa.text("DROP EXTENSION IF EXISTS vector"))
