"""
(c) 2024 Alberto Morón Hernández
"""

from collections import defaultdict

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.exceptions import (
    InvalidPasswordException,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from fastapi_users.router.common import ErrorCode
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import EmailStr, ValidationError
from typing_extensions import Annotated

from depositduck.auth import AUTH_COOKIE_NAME
from depositduck.auth.dependables import (
    InvalidPasswordReason,
    UserManager,
    get_database_strategy,
    get_user_manager,
)
from depositduck.auth.users import auth_backend, current_active_user
from depositduck.dependables import get_logger, get_settings, get_templates
from depositduck.models.auth import UserCreate
from depositduck.models.sql.auth import User
from depositduck.settings import Settings
from depositduck.utils import decrypt
from depositduck.web.templates import BootstrapClasses

auth_frontend_router = APIRouter(tags=["auth", "frontend"])
auth_operations_router = APIRouter(prefix="/auth", tags=["auth"])

LOG = get_logger()


async def htmx_redirect_to(redirect_to: str) -> Response:
    headers = {"HX-Redirect": redirect_to}
    response = Response(status_code=status.HTTP_302_FOUND, headers=headers)
    return response


async def log_user_in(
    auth_db_strategy: DatabaseStrategy, user: User, response: Response
) -> Response:
    """
    Log a given user in by generating an auth token. Store the token in a cookie
    and attach the cookie to a Response, which can be returned to the client.
    Intended to be used alongside `htmx_redirect_to()`.
    """
    token = await auth_db_strategy.write_token(user)
    response = auth_backend.transport._set_login_cookie(response, token)  # type: ignore[attr-defined]
    return response


@auth_frontend_router.get(
    "/signup/",
    summary="[htmx]",
)
async def signup(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "request": request,
        "classes_by_id": {},
    }
    return templates.TemplateResponse("auth/signup.html.jinja2", context)


@auth_operations_router.post("/register/")
async def register(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
):
    # TODO: redirect user away if already logged in.
    errors: list[str] = []
    classes_by_id: dict[str, str] = defaultdict(str)

    try:
        user_create = UserCreate(
            email=email, password=password, confirm_password=confirm_password
        )
        user = await user_manager.create(user_create, safe=True, request=request)
    except UserAlreadyExists:
        errors.append(ErrorCode.REGISTER_USER_ALREADY_EXISTS.value)
        classes_by_id["email"] += f" {BootstrapClasses.IS_INVALID.value}"
        # TODO: redirect user to /login/.
    except InvalidPasswordException as e:
        errors.extend([ErrorCode.REGISTER_INVALID_PASSWORD.value, e.reason.value])
        classes_by_id["password"] += f" {BootstrapClasses.IS_INVALID.value}"
        if e.reason.value == InvalidPasswordReason.CONFIRM_PASSWORD_DOES_NOT_MATCH:
            classes_by_id["confirm-password"] += f" {BootstrapClasses.IS_INVALID.value}"
    except ValidationError:
        errors.append("REGISTER_INVALID_EMAIL")
        classes_by_id["email"] += f" {BootstrapClasses.IS_INVALID.value}"

    try:
        await user_manager.request_verify(user)
        redirect_response = await htmx_redirect_to("/login/?prev=/auth/signup/")
        return redirect_response
    except (UserNotExists, UserInactive, UserAlreadyVerified) as e:
        LOG.warn(f"exception when initiating verification for {user}: {e}")

    for element_id, classes in classes_by_id.items():
        if BootstrapClasses.IS_INVALID not in classes:
            classes_by_id[element_id] += f" {BootstrapClasses.IS_VALID.value}"

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


@auth_operations_router.get(
    "/request-verification/",
)
async def request_verification(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    encrypted_email: str | None = Query(default=None, alias="email"),
):
    redirect_url = "/login/"

    if encrypted_email:
        redirect_url += "?prev=/auth/signup/"

        email = decrypt(settings.app_secret, encrypted_email)
        LOG.debug(f"re-verify request for [email={email}]")
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            # TODO:
            pass

        try:
            user = await user_manager.get_by_email(email)
            # TODO: implement email rate-limiting / cool-off !
            await user_manager.request_verify(user)
        except (UserNotExists, UserInactive, UserAlreadyVerified) as e:
            LOG.warn(f"exception when initiating verification for {user}: {e}")

    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@auth_operations_router.get("/verify/")
async def verify(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    token: str,
    encrypted_email: str = Query(alias="email"),
):
    redirect_url = "/login/?prev=/auth/verify/"
    try:
        await user_manager.verify(token)
        redirect_url += f"&email={encrypted_email}"
    except (InvalidVerifyToken, UserAlreadyVerified) as e:
        redirect_url += f"&email={encrypted_email}"
        email = decrypt(settings.app_secret, encrypted_email)
        if isinstance(e, InvalidVerifyToken):
            LOG.error(f"verify error - invalid token for [email={email}]")
        else:
            LOG.warn(f"verify error - already verified [email={email}]")

    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@auth_frontend_router.get(
    "/login/",
    summary="[htmx]",
)
async def login(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
    prev: str | None = None,
    next: str | None = None,
    encrypted_email: str | None = Query(default=None, alias="email"),
):
    prompt_to_reverify = False
    # value to auto-fill in the 'email' input
    user_email = ""
    if encrypted_email:
        email = decrypt(settings.app_secret, encrypted_email)
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            # TODO:
            pass
        if not user.is_verified:
            LOG.warn(f"invalid verify token for {user} - prompting to re-verify")
            prompt_to_reverify = True
        else:
            if prev == "/auth/verify/":
                user_email = user.email

    context = dict(
        request=request,
        prev_url=prev,
        next_url=next,
        prompt_to_reverify=prompt_to_reverify,
        encrypted_email=encrypted_email,
        user_email=user_email,
    )
    return templates.TemplateResponse("auth/login.html.jinja2", context)


@auth_operations_router.post("/authenticate/")
async def authenticate(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
):
    errors: list[str] = []

    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        errors.append(ErrorCode.LOGIN_BAD_CREDENTIALS.value)
        credentials.username = ""
    if user and not user.is_verified:
        errors.append(ErrorCode.LOGIN_USER_NOT_VERIFIED.value)

    if user and not errors:
        redirect_response = await htmx_redirect_to("/")
        redirect_response = await log_user_in(auth_db_strategy, user, redirect_response)
        return redirect_response

    context = dict(
        request=request,
        username=credentials.username,
        errors=errors,
    )
    return templates.TemplateResponse(
        "auth/login.html.jinja2", context=context, block_name="login_form"
    )


@auth_operations_router.post(
    "/logout/",
)
async def logout(
    user: Annotated[User, Depends(current_active_user)],
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
    request: Request,
):
    auth_cookie_token = request.cookies.get(AUTH_COOKIE_NAME)
    if auth_cookie_token:
        await auth_db_strategy.destroy_token(auth_cookie_token, user)

    response = await htmx_redirect_to("/")
    response = auth_backend.transport._set_logout_cookie(response)  # type: ignore[attr-defined]
    return response
