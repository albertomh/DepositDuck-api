"""
(c) 2024 Alberto Morón Hernández
"""

import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.engine import Row
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from depositduck.dependables import get_db_session
from depositduck.models.dto.llm import (
    SnippetCreationResponse,
    SourceTextById,
)
from depositduck.models.llm import SnippetBase
from depositduck.models.sql.llm import Snippet, SourceText

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


@llm_router.post("/snippets/fromSourceText", response_model=SnippetCreationResponse)
async def sourcetext_to_snippets(
    source_text_by_id: SourceTextById,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    sourceTextId = source_text_by_id.id
    result = await db_session.execute(select(SourceText).filter_by(id=sourceTextId))
    try:
        record: Row[tuple[SourceText]] | None = result.one_or_none()
    except MultipleResultsFound:
        raise HTTPException(
            status_code=409,
            detail=f"More than one SourceText found for [id={sourceTextId}]",
        )

    if not record:
        raise HTTPException(
            status_code=404, detail=f"SourceText [id={sourceTextId}] not found"
        )

    source_text: SourceText = record[0]
    # split on two or more consecutive newlines, removing empty strings
    paragraphs = [p for p in re.split(r"\n{2,}", source_text.content) if p]

    await db_session.execute(
        insert(Snippet),
        [
            SnippetBase(
                content=paragraph.strip(), source_text_id=sourceTextId
            ).model_dump()
            for paragraph in paragraphs
        ],
    )
    await db_session.commit()

    return SnippetCreationResponse(snippets_created_count=len(paragraphs))
