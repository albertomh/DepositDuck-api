"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from fastapi import HTTPException, Request
from jinja2.loaders import FileSystemLoader
from starlette.templating import _TemplateResponse

from depositduck.dependables import (
    AuthenticatedJinjaBlocks,
    get_db_connection_string,
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
    template_name = "home.html.jinja2"
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


def test_get_templates() -> None:
    templates = get_templates()

    assert isinstance(templates, AuthenticatedJinjaBlocks)
    loader: FileSystemLoader = templates.env.loader
    assert loader.searchpath[0].endswith("/web/templates")
