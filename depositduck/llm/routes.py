"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing_extensions import Annotated

from depositduck.dependables import get_db_session
from depositduck.models.dto.llm import SourceTextCreate
from depositduck.models.sql.llm import SourceText

llm_router = APIRouter()


@llm_router.post("/SourceText")
async def create_source_text(
    source_text: SourceTextCreate,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    data = source_text.model_dump()
    new_text = SourceText(**data)

    try:
        db_session.add(new_text)
        await db_session.commit()
        await db_session.refresh(new_text)
        return new_text

    except (IntegrityError, InvalidRequestError):
        await db_session.rollback()
