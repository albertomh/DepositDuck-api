"""
(c) 2024 Alberto Morón Hernández
"""

import httpx
import pytest
from fastapi import HTTPException, Request
from starlette.templating import _TemplateResponse

from depositduck.dependables import (
    AuthenticatedJinjaBlocks,
    get_db_connection_string,
    get_drallam_client,
    get_settings,
    get_templates,
)
from depositduck.models.sql.auth import User
from depositduck.settings import Settings


def test_get_settings():
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert vars(settings)


def test_get_db_connection_string():
    conn_str = get_db_connection_string()

    assert len(conn_str) > 0


def test_TemplateResponse_valid_context(
    mock_request: Request,
    mock_user: User,
):
    """ """
    templates = get_templates()
    template_name = "dashboard/home.html.jinja2"
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=mock_request,
        user=mock_user,
    )

    response = templates.TemplateResponse(template_name, context)

    assert isinstance(response, _TemplateResponse)
    assert list(response.context.keys()) == ["speculum_source", "request", "user"]


def test_TemplateResponse_invalid_context():
    templates = get_templates()

    with pytest.raises(HTTPException):
        templates.TemplateResponse("test.html", {})


def test_TemplateContext_default_speculum_source(mock_request: Request):
    context = AuthenticatedJinjaBlocks.TemplateContext(request=mock_request, user=None)

    settings = get_settings()
    assert (
        context.speculum_source == f"{settings.static_origin}/{settings.speculum_release}"
    )


@pytest.mark.asyncio
async def test_get_drallam_client(mock_settings):
    drallam_origin = "https://example.com"
    mock_settings.drallam_origin = drallam_origin

    dependency = get_drallam_client(settings=mock_settings)
    client = await dependency.__anext__()

    assert isinstance(client, httpx.AsyncClient)
    assert client.base_url == drallam_origin
