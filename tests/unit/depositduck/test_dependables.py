"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, timedelta

import httpx
import pytest
from fastapi import HTTPException, Request
from starlette.templating import _TemplateResponse

from depositduck.auth import TDS_DISPUTE_WINDOW_IN_DAYS
from depositduck.auth.forms.login import LoginForm
from depositduck.dependables import (
    AuthenticatedJinjaBlocks,
    get_db_connection_string,
    get_drallam_client,
    get_settings,
    get_templates,
)
from depositduck.models.sql.auth import User
from depositduck.models.sql.deposit import Tenancy
from depositduck.settings import Settings


def test_get_settings():
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert vars(settings)


def test_get_db_connection_string():
    conn_str = get_db_connection_string()

    assert len(conn_str) > 0


HOME_TEMPLATE = "dashboard/home.html.jinja2"
LOGIN_TEMPLATE = "auth/login.html.jinja2"


class TestAuthenticatedJinjaBlocks:
    def test_TemplateResponse_valid_context(
        self,
        mock_settings: Settings,
        mock_request: Request,
        mock_user: User,
    ):
        """ """
        templates = get_templates(mock_settings)
        end_date = date(2024, 7, 28)
        dispute_window_end = end_date + timedelta(days=TDS_DISPUTE_WINDOW_IN_DAYS)
        context = AuthenticatedJinjaBlocks.TemplateContext(
            request=mock_request,
            user=mock_user,
            tenancy=Tenancy(
                deposit_in_p=10000,
                end_date=end_date,
                dispute_window_end=dispute_window_end,
            ),
        )

        response = templates.TemplateResponse(HOME_TEMPLATE, context)

        assert isinstance(response, _TemplateResponse)
        assert list(response.context.keys()) == [
            "speculum_source",
            "request",
            "user",
            "tenancy",
        ]

    def test_TemplateResponse_invalid_context(self, mock_settings: Settings):
        templates = get_templates(mock_settings)

        with pytest.raises(HTTPException):
            templates.TemplateResponse("test.html", {})  # type: ignore

    def test_TemplateContext_default_speculum_source(self, mock_request: Request):
        context = AuthenticatedJinjaBlocks.TemplateContext(
            request=mock_request, user=None
        )

        settings = get_settings()
        assert (
            context.speculum_source
            == f"{settings.static_origin}/{settings.speculum_release}"
        )

    def test_TemplateResponse_no_user_in_context(
        self,
        mock_settings: Settings,
        mock_request: Request,
    ):
        templates = get_templates(mock_settings)
        context = AuthenticatedJinjaBlocks.TemplateContext(
            request=mock_request,
            user=None,
            login_form=LoginForm(username=None, password=None).for_template(),
        )

        response = templates.TemplateResponse(LOGIN_TEMPLATE, context)

        assert isinstance(response, _TemplateResponse)
        assert list(response.context.keys()) == [
            "speculum_source",
            "request",
            "user",
            "login_form",
        ]
        assert response.context["user"] is None

    def test_TemplateResponse_user_hashed_password_not_available_in_context(
        self,
        mock_settings: Settings,
        mock_request: Request,
        mock_user: User,
    ):
        mock_user.hashed_password = "some_hashed_password"
        templates = get_templates(mock_settings)
        end_date = date(2024, 7, 28)
        dispute_window_end = end_date + timedelta(days=TDS_DISPUTE_WINDOW_IN_DAYS)
        context = AuthenticatedJinjaBlocks.TemplateContext(
            request=mock_request,
            user=mock_user,
            tenancy=Tenancy(
                deposit_in_p=10000,
                end_date=end_date,
                dispute_window_end=dispute_window_end,
            ),
        )

        response = templates.TemplateResponse(HOME_TEMPLATE, context)

        assert isinstance(response, _TemplateResponse)
        assert list(response.context.keys()) == [
            "speculum_source",
            "request",
            "user",
            "tenancy",
        ]
        assert "hashed_password" not in response.context["user"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "debug",
    [
        True,
        False,
    ],
)
async def test_get_templates_debug_extension_follows_debug_setting(mock_settings, debug):
    mock_settings.debug = debug

    templates = get_templates(mock_settings)

    assert ("jinja2.ext.DebugExtension" in templates.env.extensions) == debug


@pytest.mark.asyncio
async def test_get_drallam_client(mock_settings):
    drallam_origin = "https://example.com"
    mock_settings.drallam_origin = drallam_origin

    dependency = get_drallam_client(settings=mock_settings)
    client = await dependency.__anext__()

    assert isinstance(client, httpx.AsyncClient)
    assert client.base_url == drallam_origin
