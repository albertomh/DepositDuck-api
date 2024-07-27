"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from depositduck.auth import AUTH_COOKIE_NAME
from depositduck.auth.dependables import get_database_strategy, get_user_manager
from depositduck.auth.routes import register
from depositduck.dashboard.routes import (
    current_active_user,
    db_session_factory,
)
from depositduck.dependables import get_settings, get_templates
from depositduck.models.sql.auth import User
from depositduck.models.sql.people import Prospect
from tests.unit.conftest import get_valid_settings


@pytest.mark.asyncio
async def test_unsuitable_prospect_funnel(
    web_client_factory,
    mock_async_sessionmaker,
    mock_async_session,
):
    prospect_email = "user@example.com"
    prospect_provider = "TestProvider"
    mock_add = Mock()
    mock_async_session.add = mock_add
    dependency_overrides = {
        current_active_user: lambda: None,
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        form_data = dict(email=prospect_email, providerName=prospect_provider)
        response = await client.post(
            "/auth/unsuitableProspectFunnel/",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    mock_async_sessionmaker.begin.assert_called_once()
    mock_add.assert_called_once()
    mock_add_arg = mock_add.call_args[0][0]
    assert isinstance(mock_add_arg, Prospect)
    assert mock_add_arg.email == prospect_email
    assert mock_add_arg.deposit_provider_name == prospect_provider
    assert response.status_code == status.HTTP_200_OK
    assert response.next_request is None


@pytest.mark.asyncio
async def test_register_happy_path(
    mock_async_sessionmaker,
    mock_async_session,
    mock_authenticated_jinja_blocks,
    mock_user_manager,
    mock_user,
    mock_request,
):
    """
    Check the happy path to create a new user:
      - validates and saves their email & password
      - sets the correct flags on their User
      - creates a bare-bones Tenancy object linked to the user
      - redirects the user to the login screen with the necessary query param
    """
    # arrange
    tenancy_end_date = datetime.now(timezone.utc).date()
    tenancy_end_date_str = tenancy_end_date.strftime("%Y-%m-%d")
    email = "user@example.com"
    password, confirm_password = "password", "password"
    mock_user_manager.create.return_value = mock_user

    # act
    response = await register(
        tenancy_end_date_str,
        mock_async_sessionmaker,
        mock_authenticated_jinja_blocks,
        mock_user_manager,
        None,
        mock_request,
        email,
        password,
        confirm_password,
    )

    # assert
    mock_user_manager.create.assert_awaited_once()
    user_create = mock_user_manager.create.await_args[0][0]
    assert user_create.email == email
    assert user_create.password == password
    assert user_create.is_active
    assert not user_create.is_superuser
    assert not user_create.is_verified
    mock_async_session.add.assert_called_once()
    new_tenancy = mock_async_session.add.call_args[0][0]
    assert new_tenancy.deposit_in_p == 0
    assert new_tenancy.end_date == tenancy_end_date
    assert new_tenancy.user_id == mock_user.id
    mock_user_manager.request_verify.assert_awaited_once()
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["hx-redirect"] == "/login/?prev=/auth/signup/"


@pytest.mark.asyncio
async def test_request_verification(
    web_client_factory,
    mock_user_manager,
):
    mock_settings = get_valid_settings()
    dependency_overrides = {
        get_settings: lambda: mock_settings,
        get_user_manager: lambda: mock_user_manager,
    }
    web_client = await web_client_factory(dependency_overrides=dependency_overrides)
    encrypted_email = "encrypted_email"
    decrypted_email = "user@example.com"
    mock_decrypt = Mock(return_value=decrypted_email)

    with patch("depositduck.auth.routes.decrypt", mock_decrypt):
        async with web_client as client:
            response = await client.get(
                f"/auth/requestVerification/?email={encrypted_email}",
            )

        mock_decrypt.assert_called_once_with(mock_settings.app_secret, "encrypted_email")
        mock_user_manager.get_by_email.assert_awaited_once_with(decrypted_email)
        mock_user_manager.request_verify.assert_awaited_once_with(
            mock_user_manager.get_by_email.return_value
        )
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/login/?prev=/auth/signup/"


@pytest.mark.asyncio
async def test_authenticate_happy_path(
    web_client_factory,
    mock_auth_db_strategy,
    mock_authenticated_jinja_blocks,
    mock_user_manager,
):
    username = "user@example.com"
    password = "password"
    mock_oauth2_form = OAuth2PasswordRequestForm(username=username, password=password)
    mock_user = Mock(spec=User)
    mock_user_manager.authenticate.return_value.__aenter__.return_value = mock_user

    dependency_overrides = {
        OAuth2PasswordRequestForm: lambda: mock_oauth2_form,
        get_database_strategy: lambda: mock_auth_db_strategy,
        get_templates: lambda: mock_authenticated_jinja_blocks,
        get_user_manager: lambda: mock_user_manager,
    }
    web_client = await web_client_factory(dependency_overrides=dependency_overrides)
    # mock_log_user_in = AsyncMock(return_value=mock_response)

    # with patch("depositduck.auth.routes.log_user_in", mock_log_user_in):
    async with web_client as client:
        form_data = dict(username=username, password=password)
        response = await client.post(
            "/auth/authenticate/",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    mock_user_manager.authenticate.assert_awaited_once_with(mock_oauth2_form)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["hx-redirect"] == "/"


@pytest.mark.asyncio
async def test_logout(web_client_factory, mock_user, mock_auth_db_strategy, mock_request):
    dependency_overrides = {
        current_active_user: lambda: mock_user,
        get_database_strategy: lambda: mock_auth_db_strategy,
    }
    web_client = await web_client_factory(dependency_overrides=dependency_overrides)
    auth_cookie_token = "mock_token"

    async with web_client as client:
        client.cookies.update({AUTH_COOKIE_NAME: auth_cookie_token})
        response = await client.post(
            "/auth/logout/",
        )

    mock_auth_db_strategy.destroy_token.assert_awaited_once_with(
        auth_cookie_token, mock_user
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["hx-redirect"] == "/"
