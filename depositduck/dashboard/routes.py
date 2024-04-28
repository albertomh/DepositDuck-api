"""
(c) 2024 Alberto Morón Hernández
"""

from collections import defaultdict

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.ext.asyncio import async_sessionmaker
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
from depositduck.models.sql.auth import User
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
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        classes_by_id={},
    )
    return templates.TemplateResponse("dashboard/onboarding.html.jinja2", context)


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

    # TODO: validate `name`
    #    errors.append("INVALID_NAME")

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
