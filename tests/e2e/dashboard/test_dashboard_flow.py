"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime, timedelta

import pytest
from flaky import flaky
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


@flaky(max_runs=3, min_passes=1)
@pytest.mark.asyncio
async def test_onboarding_happy_path(page: Page) -> None:
    today = datetime.today().date()
    one_year_ago = today - timedelta(weeks=52)

    await log_in_user(page, E2EUser.NEEDS_ONBOARDING, "**/welcome/")

    await expect(page.locator("//h1")).to_contain_text("Welcome!")
    onboarding_form = page.locator("#onboardingForm")
    # question: name
    await expect(
        onboarding_form.get_by_text("How should we address you?")
    ).to_be_visible()
    name_input = page.get_by_test_id("nameInput")
    await name_input.fill("Onboarder")
    await name_input.blur()
    await page.wait_for_function(
        'document.querySelector(`[data-testid="nameInput"]`).classList.contains("is-valid")'
    )
    # question: deposit amount
    await expect(onboarding_form.get_by_text("How much is your deposit?")).to_be_visible()
    deposit_input = page.get_by_test_id("depositAmountInput")
    await deposit_input.fill("924")
    await deposit_input.blur()
    await page.wait_for_function(
        'document.querySelector(`[data-testid="depositAmountInput"]`).classList.contains("is-valid")'
    )
    # question: tenancy start date
    await expect(
        onboarding_form.get_by_text("When did your tenancy start?")
    ).to_be_visible()
    start_date_input = page.get_by_test_id("tenancyStartDateInput")
    await start_date_input.fill(one_year_ago.isoformat())
    await start_date_input.blur()
    await page.wait_for_function(
        'document.querySelector(`[data-testid="tenancyStartDateInput"]`).classList.contains("is-valid")'
    )
    # question: tenancy end date
    await expect(
        onboarding_form.get_by_text("When does your tenancy end?")
    ).to_be_visible()
    await expect(page.get_by_text("You told us your tenancy ended on:")).to_be_visible()
    # TODO: make tenancy end date dynamic in e2e fixture.
    await expect(page.get_by_test_id("tenancyEndDateInput")).to_have_value("2024-04-28")
    await onboarding_form.get_by_role("button", name="Next").click()
    await page.wait_for_url("**/?prev=/welcome/")


# TODO: onboarding unhappy paths for invalid dates & their respective validation messages
