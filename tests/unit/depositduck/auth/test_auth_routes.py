"""
(c) 2024 Alberto Morón Hernández
"""

from unittest.mock import Mock

import pytest
from fastapi import status

from depositduck.auth.users import current_active_user
from depositduck.models.sql.auth import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url, auth_user, expected_status_code, next_url_path",
    [
        ("/login/", None, status.HTTP_200_OK, None),
        ("/login/", Mock(spec=User), status.HTTP_307_TEMPORARY_REDIRECT, "/"),
        ("/signup/", None, status.HTTP_200_OK, None),
        ("/signup/", Mock(spec=User), status.HTTP_307_TEMPORARY_REDIRECT, "/"),
    ],
)
async def test_auth_routes_redirect_user_based_on_authentication(
    web_client_factory, url, auth_user, expected_status_code, next_url_path
):
    dependency_overrides = {current_active_user: lambda: auth_user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get(url)

    if auth_user:
        assert response.next_request.url.path == next_url_path
    else:
        assert response.next_request is None
