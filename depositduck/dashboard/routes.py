"""
(c) 2024 Alberto Morón Hernández
"""

from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import select
from typing_extensions import Annotated

from depositduck.auth.dependables import (
    UserManager,
    get_user_manager,
)
from depositduck.auth.users import current_active_user
from depositduck.dependables import (
    AuthenticatedJinjaBlocks,
    db_session_factory,
    get_logger,
    get_templates,
)
from depositduck.middleware import frontend_auth_middleware
from depositduck.models.auth import UserUpdate
from depositduck.models.sql.auth import User
from depositduck.models.sql.deposit import Tenancy
from depositduck.web.templates import BootstrapClasses

dashboard_frontend_router = APIRouter(
    dependencies=[Depends(frontend_auth_middleware)],
    tags=["dashboard", "frontend"],
)
dashboard_operations_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

LOG = get_logger()


@dashboard_frontend_router.get(
    "/welcome/",
    summary="[htmx]",
)
async def onboarding(
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    tenancy_end_is_in_past = False
    session: AsyncSession
    async with db_session_factory.begin() as session:
        try:
            statement = select(Tenancy).filter_by(user_id=user.id)
            result = await session.execute(statement)
            tenancy: Tenancy = result.scalar_one()
            tenancy_end_date = tenancy.end_date
            tenancy_end_is_in_past = tenancy_end_date < date.today()

        except (NoResultFound, MultipleResultsFound) as e:
            LOG.warn(f"error when looking for Tenancy for {user}: {e}")

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        tenancy_end_date=tenancy_end_date,
        tenancy_end_is_in_past=tenancy_end_is_in_past,
        classes_by_id={},
    )
    return templates.TemplateResponse("dashboard/onboarding.html.jinja2", context)


@dashboard_operations_router.post("/tenancy/endDate/")
async def update_tenancy_end_date(
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    pass  # TODO:


@dashboard_operations_router.post("/completeOnboarding/")
async def complete_onboarding(
    name: Annotated[str, Form()],
    deposit_amount: Annotated[int, Form(alias="depositAmount")],
    tenancy_start_date: Annotated[str, Form(alias="tenancyStartDate")],
    tenancy_end_date: Annotated[str, Form(alias="tenancyEndDate")],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    errors: list[str] = []
    classes_by_id: dict[str, str] = defaultdict(str)

    # name
    name_has_numbers = any(char.isdigit() for char in name)
    if name_has_numbers:
        errors.append("INVALID_NAME")
    user_update = UserUpdate(first_name=name)
    await user_manager.update(user_update, user)

    # TODO: validate `end_date` is after `start_date`

    # TODO: validate `end_date` using `is_prospect_suitable()`

    fields_to_exceptions = {
        "name": ["INVALID_NAME"],
    }
    for field_id, excs in fields_to_exceptions.items():
        if set(errors).intersection(set(excs)):
            classes_by_id[field_id] += f" {BootstrapClasses.IS_INVALID.value}"
        else:
            classes_by_id[field_id] += f" {BootstrapClasses.IS_VALID.value}"

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        name=name,
        deposit_amount=deposit_amount,
        tenancy_start_date=tenancy_start_date,
        tenancy_end_date=tenancy_end_date,
        classes_by_id=classes_by_id,
        errors=errors,
    )
    return templates.TemplateResponse(
        "fragments/dashboard/onboarding/_onboarding_form.html.jinja2",
        context=context,
        block_name="onboarding_form",
    )
