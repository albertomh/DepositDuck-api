"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.router.common import ErrorCode
from jinja2_fragments.fastapi import Jinja2Blocks
from typing_extensions import Annotated

from depositduck.auth.dependables import (
    UserManager,
    get_database_strategy,
    get_user_manager,
)
from depositduck.auth.users import auth_backend
from depositduck.dependables import get_settings, get_templates
from depositduck.settings import Settings

auth_router = APIRouter()


@auth_router.get("/login")
async def login(
    settings: Annotated[Settings, Depends(get_settings)],
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html.jinja2", context)


@auth_router.post("/authenticate")
async def authenticate(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    # if requires_verification and not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
    #     )

    headers = {"HX-Redirect": "/"}
    response = Response(status_code=status.HTTP_302_FOUND, headers=headers)
    token = await auth_db_strategy.write_token(user)
    response = auth_backend.transport._set_login_cookie(response, token)  # type: ignore[attr-defined]
    return response
