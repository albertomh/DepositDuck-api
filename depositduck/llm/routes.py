"""
(c) 2024 Alberto Morón Hernández
"""

import re
from typing import Any, Iterable, Type, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from depositduck.dependables import get_db_session, get_settings
from depositduck.llm.embeddings import embed_documents
from depositduck.models.common import EntityById, TwoOhOneCreatedCount
from depositduck.models.llm import EmbeddingBase, SnippetBase
from depositduck.models.sql.llm import LLM_MODEL_TO_EMBEDDING_TABLE, Snippet, SourceText
from depositduck.settings import Settings

llm_router = APIRouter()


# TODO: unused, using scripts in `local/data_pipeline/` instead.
# @llm_router.post("/SourceText")
# async def create_source_text(
#     source_text: SourceTextCreate,
#     db_session: Annotated[AsyncSession, Depends(get_db_session)],
# ):
#     data = source_text.model_dump()
#     new_text = SourceText(**data)
#
#     try:
#         db_session.add(new_text)
#         await db_session.commit()
#         await db_session.refresh(new_text)
#         return new_text
#
#     except (IntegrityError, InvalidRequestError):
#         await db_session.rollback()


async def find_by_id(db_session: AsyncSession, T: Type[Any], id: UUID) -> SourceText:
    try:
        result = await db_session.execute(select(T).filter_by(id=id))
        record = result.scalar_one()

    except (NoResultFound, MultipleResultsFound) as e:
        status = 404 if isinstance(e, NoResultFound) else 409
        message = "zero" if isinstance(e, NoResultFound) else "more than one"
        raise HTTPException(
            status_code=status,
            detail=f"{message} {str(T)} instances for [id={id}]",
        )

    return record


@llm_router.post(
    "/snippets/fromSourceText",
    status_code=status.HTTP_201_CREATED,
    response_model=TwoOhOneCreatedCount,
)
async def snippets_from_sourcetext(
    source_text_by_id: EntityById,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        source_text: SourceText = await find_by_id(
            db_session, SourceText, source_text_by_id.id
        )
    except HTTPException:
        raise

    # split on two or more consecutive newlines, removing empty strings
    paragraphs = [p for p in re.split(r"\n{2,}", source_text.content) if p]

    await db_session.execute(
        insert(Snippet),
        [
            SnippetBase(
                content=paragraph.strip(), source_text_id=source_text.id
            ).model_dump()
            for paragraph in paragraphs
        ],
    )
    await db_session.commit()

    return TwoOhOneCreatedCount(created_count=len(paragraphs))


@llm_router.post(
    "/embeddings/fromSourceText",
    status_code=status.HTTP_201_CREATED,
    response_model=TwoOhOneCreatedCount,
)
async def embeddings_from_snippets(
    source_text_by_id: EntityById,
    settings: Annotated[Settings, Depends(get_settings)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        source_text: SourceText = await find_by_id(
            db_session, SourceText, source_text_by_id.id
        )
    except HTTPException:
        raise

    # TODO: find way to package & bake into single docker layer for portability and speed
    selected_model = settings.llm.embedding_model
    if not selected_model:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="settings.llm.embedding_model is not set",
        )

    embedding_table = LLM_MODEL_TO_EMBEDDING_TABLE.get(selected_model)
    if not embedding_table:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"could not find table for '{selected_model.name}' - "
                "check settings.llm.embedding_model"
            ),
        )

    snippets_query = await db_session.execute(
        select(Snippet).filter_by(source_text_id=source_text.id)
    )
    snippets = [s[0] for s in cast(Iterable[tuple[Snippet]], snippets_query.all())]
    if not snippets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"could not find any snippets associated with SourceText"
                f"[id={source_text_by_id.id}]"
            ),
        )
    snippets_contents = [s.content for s in cast(Iterable[Snippet], snippets)]

    embeddings = embed_documents(snippets_contents)

    await db_session.execute(
        insert(embedding_table),
        [
            EmbeddingBase(
                snippet_id=snippet.id, llm_name=selected_model.name, vector=embedding
            ).model_dump()
            for snippet, embedding in zip(snippets, embeddings)
        ],
    )
    await db_session.commit()

    return TwoOhOneCreatedCount(created_count=len(embeddings))
