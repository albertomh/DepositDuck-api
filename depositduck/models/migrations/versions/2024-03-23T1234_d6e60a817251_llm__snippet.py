"""llm__snippet

Revision ID: d6e60a817251
Revises: cb55ea348903
Create Date: 2024-03-23 12:34:01.564063

(c) 2024 Alberto Morón Hernández
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6e60a817251"
down_revision: Union[str, None] = "cb55ea348903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MODEL_TABLE_NAMES = [
    "embedding_minilm_l6_v2",
    "embedding_minilm_l6_multiqa",
]


def upgrade() -> None:
    op.create_table(
        "llm__snippet",
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_text_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_text_id"],
            ["llm__source_text.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    for model in MODEL_TABLE_NAMES:
        op.add_column(
            f"llm__{model}",
            sa.Column("snippet_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        )
        op.create_foreign_key(
            None, f"llm__{model}", "llm__snippet", ["snippet_id"], ["id"]
        )


def downgrade() -> None:
    op.drop_table("llm__snippet")
