"""
(c) 2024 Alberto Morón Hernández
"""

import httpx
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import Annotated

from depositduck.dependables import db_session_factory, get_settings, get_speculum_client
from depositduck.settings import Settings

api_router = APIRouter()


class ServiceStatus(BaseModel):
    is_ok: bool
    message: str | None = None
    error: str | None = None


class ServicesSummary(BaseModel):
    database: ServiceStatus
    static_assets: ServiceStatus


@api_router.get(
    "/healthz",
    summary="Check status of the webapp and services DepositDuck depends on",
    tags=["ops"],
)
async def healthz(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    get_speculum_client: Annotated[httpx.AsyncClient, Depends(get_speculum_client)],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
):
    status_summary = ServicesSummary(
        database=ServiceStatus(is_ok=True),
        static_assets=ServiceStatus(is_ok=True),
    )

    try:
        res = await get_speculum_client.head("/css/main.min.css")
        res.raise_for_status()
        status_summary.static_assets.message = (
            f"'{res.url}' returned HTTP {res.status_code}"
        )
    except httpx.HTTPError as e:
        status_summary.static_assets.is_ok = False
        status_summary.static_assets.error = str(e)

    try:
        session: AsyncSession
        async with db_session_factory.begin() as session:
            result = await session.execute(select(1))
            if result.scalar_one() != 1:
                raise SQLAlchemyError("database failed 'SELECT(1)' check")
    except SQLAlchemyError as e:
        status_summary.database.is_ok = False
        status_summary.database.error = str(e)

    status_code = status.HTTP_200_OK
    summary_data = status_summary.model_dump(exclude_none=True)
    has_error = any(value.get("is_ok", False) is False for value in summary_data.values())
    if has_error:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(summary_data, status_code=status_code)
