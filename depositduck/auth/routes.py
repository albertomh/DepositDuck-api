"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime

from cryptography.fernet import InvalidToken
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
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import Annotated

from depositduck.auth import (
    AUTH_COOKIE_NAME,
    TenancyEndDateOutOfRange,
    is_prospect_suitable,
)
from depositduck.auth.dependables import (
    InvalidPasswordReason,
    UserManager,
    get_database_strategy,
    get_user_manager,
)
from depositduck.auth.forms.login import (
    LoginBadCredentials,
    LoginForm,
    UserNotVerified,
    VerificationLinkExpired,
)
from depositduck.auth.forms.signup import (
    ConfirmPasswordDoesNotMatch,
    FilterProspectForm,
    PasswordTooShort,
    SignupForm,
)
from depositduck.auth.forms.unsuitable_prospect_funnel import UnsuitableProspectForm
from depositduck.auth.users import auth_backend, current_active_user
from depositduck.dependables import (
    AuthenticatedJinjaBlocks,
    db_session_factory,
    get_logger,
    get_settings,
    get_templates,
)
from depositduck.forms.validators import InvalidEmail
from depositduck.middleware import frontend_auth_middleware, operations_auth_middleware
from depositduck.models.auth import UserCreate
from depositduck.models.sql.auth import User
from depositduck.models.sql.deposit import Tenancy
from depositduck.models.sql.people import Prospect
from depositduck.settings import Settings
from depositduck.utils import (
    date_from_iso8601_str,
    days_between_dates,
    decrypt,
    htmx_redirect_to,
)

auth_frontend_router = APIRouter(
    dependencies=[Depends(frontend_auth_middleware)],
    tags=["auth", "frontend"],
)
auth_operations_router = APIRouter(
    prefix="/auth",
    dependencies=[Depends(operations_auth_middleware)],
    tags=["auth"],
)

LOG = get_logger()


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
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    filter_prospect_form = FilterProspectForm(
        provider_choice=None,
        tenancy_end_date=None,
    )

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        filter_prospect_form=filter_prospect_form.for_template(),
    )
    return templates.TemplateResponse("auth/signup.html.jinja2", context)


@auth_operations_router.post("/filterProspect/validateForm/")
async def validate_filter_prospect_form(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    field: str | None = None,
    provider_choice: Annotated[str | None, Form(alias="providerChoice")] = None,
    tenancy_end_date_str: Annotated[str | None, Form(alias="tenancyEndDate")] = None,
):
    tenancy_end_date = None
    if tenancy_end_date_str:
        tenancy_end_date = await date_from_iso8601_str(tenancy_end_date_str)
    filter_prospect_form = FilterProspectForm(
        provider_choice=provider_choice,
        tenancy_end_date=tenancy_end_date,
    )

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        filter_prospect_form=filter_prospect_form.for_template(),
    )

    template = "fragments/auth/signup/_filter_prospect_form.html.jinja2"
    block_name = "filter_prospect_form"
    if field is not None:
        block_name += f"__{field}"
    field_response = templates.TemplateResponse(
        template,
        context,
        block_name=block_name,
    )
    submit_button_response = templates.TemplateResponse(
        template,
        context,
        block_name="submit_button",
    )
    combined_html = field_response.body.decode() + submit_button_response.body.decode()
    return Response(content=combined_html, media_type="text/html")


@auth_operations_router.post("/filterProspect/")
async def filter_prospect_for_signup(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    provider_choice: Annotated[str | None, Form(alias="providerChoice")] = None,
    tenancy_end_date_str: Annotated[str | None, Form(alias="tenancyEndDate")] = None,
):
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        is_suitable_prospect=False,
        provider_choice=provider_choice,
    )

    tenancy_end_date = None
    if tenancy_end_date_str:
        tenancy_end_date = await date_from_iso8601_str(tenancy_end_date_str)
    if provider_choice is None or tenancy_end_date is None:
        filter_prospect_form = FilterProspectForm(
            provider_choice=provider_choice,
            tenancy_end_date=tenancy_end_date,
        )
        context.filter_prospect_form = filter_prospect_form.for_template()
        return templates.TemplateResponse(
            "fragments/auth/signup/_filter_prospect_form.html.jinja2", context
        )

    today = datetime.today().date()
    context.days_since_end_date = days_between_dates(today, tenancy_end_date)

    context.tenancy_end_date = tenancy_end_date_str
    context.end_date_is_within_range = True
    try:
        context.is_suitable_prospect = await is_prospect_suitable(
            provider_choice, None, tenancy_end_date
        )
        signup_form = SignupForm(
            email=None,
            password=None,
            confirm_password=None,
        )
        context.signup_form = signup_form.for_template()
        response = templates.TemplateResponse(
            "fragments/auth/signup/_signup_user_form.html.jinja2", context
        )
        query = "step=register"
    except ExceptionGroup as eg:
        for exc in eg.exceptions:
            LOG.info(str(exc))
            if isinstance(exc, TenancyEndDateOutOfRange):
                context.end_date_is_within_range = False

        unsuitable_prospect_form = UnsuitableProspectForm(
            email=None,
            provider_name=None,
        )
        context.unsuitable_prospect_form = unsuitable_prospect_form.for_template()
        response = templates.TemplateResponse(
            "fragments/auth/signup/_filter_prospect_reject.html.jinja2", context
        )
        query = "step=funnel"

    response.headers.update({"HX-Replace-Url": f"/signup/?{query}"})
    return response


@auth_operations_router.post("/unsuitableProspectFunnel/validateForm/")
async def validate_unsuitable_prospect_funnel_form(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    field: str | None = None,
    email: Annotated[str | None, Form()] = None,
    provider_name: Annotated[str | None, Form(alias="providerName")] = None,
):
    unsuitable_prospect_form = UnsuitableProspectForm(
        email=email,
        provider_name=provider_name,
    )

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        unsuitable_prospect_form=unsuitable_prospect_form.for_template(),
        has_submitted_funnel_form=False,
    )

    template = "fragments/auth/signup/_filter_prospect_reject.html.jinja2"
    block_name = "unsuitable_prospect_funnel"
    if field is not None:
        block_name += f"__{field}"
    field_response = templates.TemplateResponse(
        template,
        context=context,
        block_name=block_name,
    )
    submit_button_response = templates.TemplateResponse(
        template,
        context,
        block_name="submit_button",
    )
    combined_html = field_response.body.decode() + submit_button_response.body.decode()
    return Response(content=combined_html, media_type="text/html")


@auth_operations_router.post("/unsuitableProspectFunnel/")
async def unsuitable_prospect_funnel(
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    email: Annotated[str | None, Form()] = None,
    provider_name: Annotated[str | None, Form(alias="providerName")] = None,
):
    unsuitable_prospect_form = UnsuitableProspectForm(
        email=email,
        provider_name=provider_name,
    )

    try:
        prospect = Prospect(email=email, deposit_provider_name=provider_name)
        session: AsyncSession
        async with db_session_factory.begin() as session:
            session.add(prospect)
    except (ValueError, SQLAlchemyError) as e:
        LOG.error(f"error when trying to record prospect [{email}]: {str(e)}")

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        unsuitable_prospect_form=unsuitable_prospect_form.for_template(),
        has_submitted_funnel_form=True,
    )
    return templates.TemplateResponse(
        "fragments/auth/signup/_filter_prospect_reject.html.jinja2",
        context=context,
        block_name="unsuitable_prospect_funnel",
    )


@auth_operations_router.post("/signup/validateForm/")
async def validate_signup_form(
    tenancy_end_date_str: Annotated[str, Form(alias="tenancyEndDate")],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    field: str | None = None,
    email: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    confirm_password: Annotated[str | None, Form(alias="confirmPassword")] = None,
):
    signup_form = SignupForm(
        email=email,
        password=password,
        confirm_password=confirm_password,
    )

    if password is not None:
        try:
            await user_manager.validate_password(password)
        except InvalidPasswordException as e:
            if e.reason == InvalidPasswordReason.PASSWORD_TOO_SHORT:
                signup_form.fields.add_error("password", PasswordTooShort, password)
        if confirm_password is not None and confirm_password != password:
            signup_form.fields.add_error(
                "confirm_password", ConfirmPasswordDoesNotMatch, confirm_password
            )

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        tenancy_end_date=tenancy_end_date_str,
        signup_form=signup_form.for_template(),
    )

    template = "fragments/auth/signup/_signup_user_form.html.jinja2"
    block_name = "signup_form"
    if field is not None:
        block_name += f"__{field}"
    field_response = templates.TemplateResponse(
        template,
        context=context,
        block_name=block_name,
    )
    context.oob_submit_button = True
    submit_button_response = templates.TemplateResponse(
        template,
        context,
        block_name="submit_button",
    )
    combined_html = field_response.body.decode() + submit_button_response.body.decode()
    return Response(content=combined_html, media_type="text/html")


@auth_operations_router.post("/register/")
async def register(
    tenancy_end_date_str: Annotated[str, Form(alias="tenancyEndDate")],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    email: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    confirm_password: Annotated[str | None, Form(alias="confirmPassword")] = None,
):
    signup_form = SignupForm(
        email=email,
        password=password,
        confirm_password=confirm_password,
    )

    try:
        user_create = UserCreate(
            email=email, password=password, confirm_password=confirm_password
        )
        new_user = await user_manager.create(user_create, safe=True, request=request)
    except UserAlreadyExists:
        redirect_to_login = await htmx_redirect_to("/login/?prev=existingUser")
        return redirect_to_login
    except InvalidPasswordException:
        signup_form.fields.add_error("password", PasswordTooShort, password)
    except ValidationError:
        signup_form.fields.add_error("email", InvalidEmail, email)

    if new_user is not None:
        try:
            if tenancy_end_date_str:
                tenancy_end_date = await date_from_iso8601_str(tenancy_end_date_str)
            tenancy = Tenancy(
                deposit_in_p=0, end_date=tenancy_end_date, user_id=new_user.id
            )
            session: AsyncSession
            async with db_session_factory.begin() as session:
                session.add(tenancy)
        except (ValueError, SQLAlchemyError) as e:
            LOG.error(f"error when trying to record tenancy for {new_user}: {str(e)}")

        try:
            await user_manager.request_verify(new_user)
            redirect_to_login = await htmx_redirect_to("/login/?prev=/auth/signup/")
            return redirect_to_login
        except (UserNotExists, UserInactive, UserAlreadyVerified) as e:
            LOG.warn(f"exception when initiating verification for {new_user}: {e}")
            if isinstance(e, UserAlreadyVerified):
                redirect_to_login = await htmx_redirect_to("/login/?prev=existingUser")
                return redirect_to_login

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        signup_form=signup_form.for_template(),
    )
    return templates.TemplateResponse(
        "fragments/auth/signup/_signup_user_form.html.jinja2",
        context=context,
        block_name="signup_form",
    )


@auth_operations_router.get(
    "/requestVerification/",
)
async def request_verification(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    encrypted_email: str | None = Query(default=None, alias="email"),
):
    redirect_path = "/login/"

    if encrypted_email:
        redirect_path += "?prev=/auth/signup/"
        email = decrypt(settings.app_secret, encrypted_email)
        LOG.debug(f"re-verify request for [{email=}]")

        try:
            user = await user_manager.get_by_email(email)
            # TODO: implement email rate-limiting / cool-off !
            await user_manager.request_verify(user)
        except (UserNotExists, UserInactive, UserAlreadyVerified) as e:
            if isinstance(e, UserNotExists):
                LOG.warn(f"re-verify request for inexistent user [{email=}]")
            else:
                LOG.warn(f"exception when requesting verification for {user}: {e}")

    return RedirectResponse(redirect_path, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@auth_operations_router.get("/verify/")
async def verify(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    token: str,
    encrypted_email: str = Query(alias="email"),
):
    redirect_path = "/login/?prev=/auth/verify/"
    try:
        await user_manager.verify(token)
        redirect_path += f"&email={encrypted_email}"
    except (InvalidVerifyToken, UserAlreadyVerified) as e:
        redirect_path += f"&email={encrypted_email}"
        try:
            email = decrypt(settings.app_secret, encrypted_email)
            if isinstance(e, InvalidVerifyToken):
                LOG.error(f"verify error - invalid token for [{email=}]")
            else:
                LOG.warn(f"verify error - already verified [{email=}]")
        except InvalidToken:
            LOG.error(f"verify error - encrypted email [{encrypted_email=}]")

    return RedirectResponse(redirect_path, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@auth_frontend_router.get(
    "/login/",
    summary="[htmx]",
)
async def login(
    settings: Annotated[Settings, Depends(get_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    user: Annotated[User, Depends(current_active_user)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    request: Request,
    prev: str | None = None,
    next: str = "/",
    encrypted_email: str | None = Query(default=None, alias="email"),
):
    login_form = LoginForm(
        username=None,
        password=None,
    )

    if encrypted_email:
        email = decrypt(settings.app_secret, encrypted_email)
        try:
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            login_form.fields.add_error("username", UserNotExists, email)
        if not user.is_verified:
            login_form.fields.add_error("username", VerificationLinkExpired, email)
            LOG.warn(f"invalid verify token for {user} - prompting to re-verify")
        else:
            if prev == "/auth/verify/":
                login_form.user_input["username"] = user.email

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        # avoid showing authenticated navbar to users following verification links
        user=None,
        prev_path=prev,
        next_path=next,
        encrypted_email=encrypted_email,
        login_form=login_form.for_template(),
    )

    return templates.TemplateResponse(
        "auth/login.html.jinja2",
        context,
    )


@auth_operations_router.post("/authenticate/")
async def authenticate(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_db_strategy: Annotated[DatabaseStrategy, Depends(get_database_strategy)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
    next: str = "/",
):
    login_form = LoginForm(
        username=credentials.username,
        password=credentials.password,
    )

    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        login_form.fields.add_error("username", LoginBadCredentials, credentials.username)
        login_form.user_input["username"] = ""
    elif user and not user.is_verified:
        login_form.fields.add_error("username", UserNotVerified, credentials.username)

    if user and login_form.can_submit:
        redirect_to_next = await htmx_redirect_to(next)
        redirect_to_next = await log_user_in(auth_db_strategy, user, redirect_to_next)
        return redirect_to_next

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        login_form=login_form.for_template(),
    )
    return templates.TemplateResponse(
        "auth/login.html.jinja2", context=context, block_name="main"
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
