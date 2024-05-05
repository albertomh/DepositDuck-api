"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime, timezone

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
from depositduck.dashboard.forms import OnboardingForm
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
from depositduck.utils import date_from_iso8601_str, htmx_redirect_to

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
    session: AsyncSession
    async with db_session_factory.begin() as session:
        try:
            statement = select(Tenancy).filter_by(user_id=user.id)
            result = await session.execute(statement)
            tenancy: Tenancy = result.scalar_one()
            tenancy_end_date = tenancy.end_date

        except (NoResultFound, MultipleResultsFound) as e:
            LOG.warn(f"error when looking for Tenancy for {user}: {e}")

    onboarding_form = OnboardingForm(
        name=None,
        deposit_amount=None,
        tenancy_start_date=None,
        tenancy_end_date=tenancy_end_date,
    )
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        onboarding_form=onboarding_form.for_template(),
    )
    return templates.TemplateResponse("dashboard/onboarding.html.jinja2", context)


@dashboard_operations_router.post(
    "/onboarding/form/validate/",
    summary="[htmx]",
)
async def validate_onboarding_form(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    name: Annotated[str | None, Form()] = None,
    deposit_amount: Annotated[int | None, Form(alias="depositAmount")] = None,
    tenancy_start_date_str: Annotated[str | None, Form(alias="tenancyStartDate")] = None,
    tenancy_end_date_str: Annotated[str | None, Form(alias="tenancyEndDate")] = None,
):
    tenancy_start_date = None
    if tenancy_start_date_str:
        tenancy_start_date = await date_from_iso8601_str(tenancy_start_date_str)
    tenancy_end_date = None
    if tenancy_end_date_str:
        tenancy_end_date = await date_from_iso8601_str(tenancy_end_date_str)
    onboarding_form = OnboardingForm(
        name=name,
        deposit_amount=deposit_amount,
        tenancy_start_date=tenancy_start_date,
        tenancy_end_date=tenancy_end_date,
    )

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request, user=user, onboarding_form=onboarding_form.for_template()
    )

    return templates.TemplateResponse(
        "fragments/dashboard/onboarding/_onboarding_form.html.jinja2",
        context,
        block_name="onboarding_form",
    )


@dashboard_operations_router.post("/completeOnboarding/")
async def complete_onboarding(
    name: Annotated[str, Form()],
    deposit_amount: Annotated[int, Form(alias="depositAmount")],
    tenancy_start_date_str: Annotated[str, Form(alias="tenancyStartDate")],
    tenancy_end_date_str: Annotated[str, Form(alias="tenancyEndDate")],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    tenancy_start_date = await date_from_iso8601_str(tenancy_start_date_str)
    tenancy_end_date = await date_from_iso8601_str(tenancy_end_date_str)
    onboarding_form = OnboardingForm(
        name=name,
        deposit_amount=deposit_amount,
        tenancy_start_date=tenancy_start_date,
        tenancy_end_date=tenancy_end_date,
    )

    if not onboarding_form.can_submit:
        context = AuthenticatedJinjaBlocks.TemplateContext(
            request=request, user=user, onboarding_form=onboarding_form.for_template()
        )
        return templates.TemplateResponse(
            "fragments/dashboard/onboarding/_onboarding_form.html.jinja2",
            context,
            block_name="onboarding_form",
        )

    user_update = UserUpdate(
        first_name=name, completed_onboarding_at=datetime.now(timezone.utc)
    )
    await user_manager.update(user_update, user)

    session: AsyncSession
    async with db_session_factory.begin() as session:
        try:
            statement = select(Tenancy).filter_by(user_id=user.id)
            result = await session.execute(statement)
            tenancy: Tenancy = result.scalar_one()
            tenancy.deposit_in_p = deposit_amount * 100
            tenancy.start_date = tenancy_start_date

        except (NoResultFound, MultipleResultsFound) as e:
            LOG.warn(f"error when looking for Tenancy for {user}: {e}")

    redirect_to_dashboard = await htmx_redirect_to("/?prev=/welcome/")
    return redirect_to_dashboard
