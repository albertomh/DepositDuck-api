"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists
from fastapi_users.router.common import ErrorCode
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import ValidationError
from structlog._config import BoundLoggerLazyProxy
from typing_extensions import Annotated

from depositduck.auth.dependables import (
    UserManager,
    get_database_strategy,
    get_user_manager,
)
from depositduck.auth.users import auth_backend
from depositduck.dependables import get_logger, get_templates
from depositduck.models.auth import UserCreate

auth_frontend_router = APIRouter(tags=["auth", "frontend"])
auth_operations_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_frontend_router.get("/signup/")
async def signup(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("auth/signup.html.jinja2", context)


@auth_operations_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    LOG: Annotated[BoundLoggerLazyProxy, Depends(get_logger)],
    request: Request,
):
    try:
        user_create = UserCreate(email=username, password=password)
        created_user = await user_manager.create(user_create, safe=True, request=request)
        LOG.debug(created_user.__dict__)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_INVALID_EMAIL",
        )
    return Response(status_code=status.HTTP_201_CREATED)


@auth_frontend_router.get("/login/")
async def login(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("auth/login.html.jinja2", context)


@auth_operations_router.post("/authenticate/")
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
