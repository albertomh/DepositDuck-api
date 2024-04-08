"""
(c) 2024 Alberto Morón Hernández
"""

from collections import defaultdict

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists
from fastapi_users.router.common import ErrorCode
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import ValidationError
from typing_extensions import Annotated

from depositduck.auth.dependables import (
    InvalidPasswordReason,
    UserManager,
    get_database_strategy,
    get_user_manager,
)
from depositduck.auth.users import auth_backend
from depositduck.dependables import get_logger, get_templates
from depositduck.models.auth import UserCreate
from depositduck.models.sql.auth import User
from depositduck.web.templates import BootstrapClasses

auth_frontend_router = APIRouter(tags=["auth", "frontend"])
auth_operations_router = APIRouter(prefix="/auth", tags=["auth"])

LOG = get_logger()


async def log_user_in_and_redirect(
    auth_db_strategy: DatabaseStrategy, user: User, redirect_to: str
) -> Response:
    """
    Log a given user in returning a HTTP 302 response with a fresh auth cookie attached
    to it. Redirect to the specified path.
    """
    headers = {"HX-Redirect": redirect_to}
    response = Response(status_code=status.HTTP_302_FOUND, headers=headers)
    token = await auth_db_strategy.write_token(user)
    response = auth_backend.transport._set_login_cookie(response, token)  # type: ignore[attr-defined]
    return response


@auth_frontend_router.get("/signup/")
async def signup(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "request": request,
        "classes_by_id": [],
    }
    return templates.TemplateResponse("auth/signup.html.jinja2", context)


@auth_operations_router.post("/register/")
async def register(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
    request: Request,
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    # TODO: redirect user away if already logged in.
    errors: list[str] = []
    classes_by_id: dict[str, str] = defaultdict(str)

    try:
        user_create = UserCreate(
            email=email, password=password, confirm_password=confirm_password
        )
        created_user = await user_manager.create(user_create, safe=True, request=request)
        redirect_response = await log_user_in_and_redirect(
            auth_db_strategy, created_user, "/"
        )
        return redirect_response
    except UserAlreadyExists:
        errors.append(ErrorCode.REGISTER_USER_ALREADY_EXISTS.value)
        classes_by_id["email"] += BootstrapClasses.IS_INVALID
        # TODO: redirect user to /login/.
    except InvalidPasswordException as e:
        errors.extend([ErrorCode.REGISTER_INVALID_PASSWORD.value, e.reason.value])
        if e.reason.value == InvalidPasswordReason.CONFIRM_PASSWORD_DOES_NOT_MATCH:
            classes_by_id["confirm-password"] += BootstrapClasses.IS_INVALID
        else:
            classes_by_id["password"] += BootstrapClasses.IS_INVALID
    except ValidationError:
        errors.append("REGISTER_INVALID_EMAIL")
        classes_by_id["email"] += BootstrapClasses.IS_INVALID

    for _, classes in classes_by_id.items():
        if BootstrapClasses.IS_INVALID not in classes:
            classes += BootstrapClasses.IS_VALID

    LOG.debug(errors)
    context = dict(
        request=request,
        email=email,
        password=password,
        classes_by_id=classes_by_id,
        errors=errors,
    )
    return templates.TemplateResponse(
        "auth/signup.html.jinja2", context=context, block_name="signup_form"
    )


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
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    # TODO: look at POST /register/ above and follow error-handling HTMX fragments pattern
    # if requires_verification and not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
    #     )

    redirect_response = await log_user_in_and_redirect(auth_db_strategy, user, "/")
    return redirect_response
