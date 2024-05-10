"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from playwright.async_api import Page, expect

from tests.e2e.conftest import APP_ORIGIN, E2EUser, log_in_user


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user, expected_path",
    [
        (E2EUser.ACTIVE_VERIFIED, "/"),
        (E2EUser.NEEDS_ONBOARDING, "/welcome/"),
    ],
)
async def test_redirect_to_onboarding_when_needed(
    page: Page, user, expected_path
) -> None:
    await log_in_user(page, user, expected_path)
    await expect(page).to_have_url(f"{APP_ORIGIN}{expected_path}")


# TODO: onboarding flow happy path

# TODO: onboarding unhappy paths for invalid dates & their respective validation messages
