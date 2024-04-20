"""
(c) 2024 Alberto Morón Hernández
"""

import re
from typing import Any, Iterable, Type, cast
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from typing_extensions import Annotated

from depositduck.dependables import db_session_factory, get_drallam_client, get_settings
from depositduck.llm.embeddings import embed_document
from depositduck.models.common import EntityById, TwoOhOneCreatedCount
from depositduck.models.llm import NOMIC, EmbeddingBase, SnippetBase
from depositduck.models.sql.llm import EmbeddingNomic, Snippet, SourceText
from depositduck.settings import Settings

llm_router = APIRouter()


async def find_by_id(db_session: AsyncSession, T: Type[Any], id: UUID) -> SourceText:
    try:
        result = await db_session.execute(select(T).filter_by(id=id))
        record = result.scalar_one()

    except (NoResultFound, MultipleResultsFound) as e:
        if isinstance(e, NoResultFound):
            status_code = status.HTTP_404_NOT_FOUND
            message = "zero"
        else:
            status_code = status.HTTP_409_CONFLICT
            message = "more than one"
        raise HTTPException(
            status_code=status_code,
            detail=f"{message} {str(T)} instances for [id={id}]",
        )

    return record


@llm_router.post(
    "/snippets/fromSourceText",
    summary="Generate Snippets from a SourceText",
    status_code=status.HTTP_201_CREATED,
    response_model=TwoOhOneCreatedCount,
)
async def snippets_from_sourcetext(
    source_text_by_id: EntityById,
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
):
    """
    Given a SourceText in the database, split it and save as Snippet records.

    _Arguments:_
    - **id (UUID)**: the id of a SourceText record in the database

    _Returns:_
    - a count of how many Snippet records were saved to the database
    """
    session: AsyncSession
    try:
        async with db_session_factory.begin() as session:
            source_text: SourceText = await find_by_id(
                session, SourceText, source_text_by_id.id
            )
    except HTTPException:
        raise

    # split on two or more consecutive newlines, removing empty strings
    paragraphs = [p for p in re.split(r"\n{2,}", source_text.content) if p]

    try:
        async with db_session_factory.begin() as session:
            await session.execute(
                insert(Snippet),
                [
                    SnippetBase(
                        content=paragraph.strip(), source_text_id=source_text.id
                    ).model_dump()
                    for paragraph in paragraphs
                ],
            )
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e._message))

    return TwoOhOneCreatedCount(created_count=len(paragraphs))


@llm_router.post(
    "/embeddings/fromSourceText",
    summary="Generate embeddings for all Snippets associated with a SourceText",
    status_code=status.HTTP_201_CREATED,
    response_model=TwoOhOneCreatedCount,
)
async def embeddings_from_snippets(
    source_text_by_id: EntityById,
    settings: Annotated[Settings, Depends(get_settings)],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    drallam_client: Annotated[httpx.AsyncClient, Depends(get_drallam_client)],
):
    """
    Given a SourceText that has been split into Snippets, generate embeddings for each
    Snippet.

    _Arguments:_
    - **id (UUID)**: the id of a SourceText record in the database

    _Returns:_
    - **created_count (int)**: a count of how many Snippet records were saved to the
    database
    """
    session: AsyncSession
    try:
        async with db_session_factory.begin() as session:
            source_text: SourceText = await find_by_id(
                session, SourceText, source_text_by_id.id
            )
    except HTTPException:
        raise

    async with db_session_factory.begin() as session:
        snippets_query = await session.execute(
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

    embeddings = [
        await embed_document(settings, drallam_client, doc) for doc in snippets_contents
    ]

    async with db_session_factory.begin() as session:
        await session.execute(
            insert(EmbeddingNomic),
            [
                EmbeddingBase(
                    snippet_id=snippet.id, llm_name=NOMIC.name, vector=embedding
                ).model_dump()
                for snippet, embedding in zip(snippets, embeddings)
            ],
        )

    return TwoOhOneCreatedCount(created_count=len(embeddings))


@llm_router.get(
    "/snippets/relevantToQuery",
    summary="Return Snippets relevant to a user query",
    response_model=list[str],
)
async def find_snippets_relevant_to_query(
    settings: Annotated[Settings, Depends(get_settings)],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    drallam_client: Annotated[httpx.AsyncClient, Depends(get_drallam_client)],
    query: str = Query(..., title="query", description=""),
    max_snippets: int = Query(5, title="max", description=""),
) -> list[str]:
    """
    Given a user query, return relevant records from the corpus of Snippets.
    Performs a vector similarity search.

    _Arguments:_
    - **query (str)**: user query to find relevant Snippets for
    - **max_snippets (Optional[int])**: maximum relevant Snippets to return - maximum 10

    _Returns:_
    - **list[str]**: Snippets in order of decreasing relevance, up to a count of
      max_snippets
    """
    default_max_snippets = 10
    if max_snippets > default_max_snippets:
        max_snippets = default_max_snippets

    query_embedding = await embed_document(settings, drallam_client, query)

    session: AsyncSession
    async with db_session_factory.begin() as session:
        neighbours = await session.scalars(
            select(EmbeddingNomic)
            .order_by(EmbeddingNomic.vector.l2_distance(query_embedding))  # type: ignore[attr-defined]
            .limit(max_snippets)
            .options(selectinload(EmbeddingNomic.snippet))  # type: ignore[arg-type]
        )
    return [n.snippet.content for n in neighbours]
