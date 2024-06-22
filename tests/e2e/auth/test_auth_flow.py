"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime, timedelta

import pytest
from bs4 import BeautifulSoup
from playwright.async_api import Page, expect

from tests.e2e.conftest import APP_ORIGIN, E2E_USER_PASSWORD, E2EUser, log_in_user
from tests.e2e.mailhog_utils import get_mailhog_email


@pytest.mark.asyncio
async def test_navbar_logged_out(page: Page) -> None:
    await page.goto(f"{APP_ORIGIN}/")
    navbar = page.get_by_role("navigation")
    await expect(navbar).to_be_visible()
    await expect(navbar.get_by_role("button", name="Log in")).to_be_visible()
    await expect(navbar.get_by_role("button", name="Sign up")).to_be_visible()
    await expect(navbar.get_by_role("img")).to_have_attribute(
        "alt", "The DepositDuck wordmark, with the Sterling duck mascot"
    )


@pytest.mark.asyncio
async def test_navbar_logged_in(page: Page) -> None:
    await log_in_user(page, E2EUser.ACTIVE_VERIFIED)
    await expect(page.get_by_test_id("navbarAccountDropdown")).to_be_visible()
    await page.get_by_test_id("navbarAccountDropdown").click()
    await expect(
        page.get_by_test_id("navbarAccountDropdown").get_by_role("list")
    ).to_have_count(1)
    await expect(page.get_by_text("Log out")).to_be_visible()


@pytest.mark.asyncio
async def test_sign_up_happy_path(page: Page) -> None:
    email = "happy_path@example.com"
    password = "MyPassword"
    today = datetime.today().date()
    one_month_ago = today - timedelta(weeks=4)

    await page.goto(f"{APP_ORIGIN}/")
    await page.get_by_role("button", name="Sign up").click()
    await expect(page.get_by_role("heading", name="Sign up")).to_be_visible()
    # fill out first half of sign-up form (prospect filter)
    filter_prospect_form = page.locator("#filterProspectForm")
    await expect(
        filter_prospect_form.get_by_text("Who is your deposit registered with?")
    ).to_be_visible()
    tds_radio = page.get_by_role("button", name="Tenancy Deposit Scheme (TDS)")
    await expect(tds_radio).to_be_visible()
    await expect(
        filter_prospect_form.get_by_role("button", name="A different provider")
    ).to_be_visible()
    await expect(
        filter_prospect_form.get_by_text("When does your tenancy end?")
    ).to_be_visible()
    await tds_radio.click()
    await page.get_by_test_id("tenancyEndDateInput").fill(one_month_ago.isoformat())
    await filter_prospect_form.get_by_role("button", name="Next").click()
    # fill out second half of sign-up form (register new user)
    await page.wait_for_url("**/signup/?step=register")
    await expect(page.get_by_text("Deposit held by TDS")).to_be_visible()
    await expect(
        page.get_by_text(f"Tenancy ended on {one_month_ago.isoformat()}")
    ).to_be_visible()
    email_input = page.get_by_label("Email:")
    await email_input.fill(email)
    await email_input.blur()
    await page.wait_for_function(
        "document.querySelector('input#email').classList.contains('is-valid')"
    )
    password_input = page.get_by_label("Password:", exact=True)
    await password_input.fill(password)
    await password_input.blur()
    await page.wait_for_function(
        "document.querySelector('input#password').classList.contains('is-valid')"
    )
    confirm_password_input = page.get_by_label("Confirm password:")
    await confirm_password_input.fill(password)
    await confirm_password_input.blur()
    await page.wait_for_function(
        "document.querySelector('input#confirm-password').classList.contains('is-valid')"
    )
    await confirm_password_input.blur()
    sign_up_form = page.locator("#signupForm")
    await sign_up_form.get_by_role("button", name="Sign up").click()
    await page.wait_for_url("**/login/?prev=/auth/signup/")
    await expect(page.locator("//h1")).to_contain_text("Log in")
    # check user prompted to find verification email
    card = page.get_by_test_id("cardPleaseVerify")
    await expect(card.get_by_role("heading")).to_contain_text("Please verify your email")
    await expect(
        card.get_by_text(
            "Please follow the link in the email we have sent you to verify your account "
            "before logging in"
        )
    ).to_be_visible()
    # check verification email and follow verification link
    mh_email = await get_mailhog_email()
    assert mh_email.Content.Headers.Subject == ["Your DepositDuck account verification"]
    soup = BeautifulSoup(mh_email.Content.Body, "html.parser")
    verify_anchor = soup.find("a", attrs={"data-testid": "linkToVerify"})
    verify_url = verify_anchor["href"]
    await page.goto(verify_url)
    assert "/login" in page.url
    await expect(page.locator("//h1")).to_contain_text("Log in")
    card = page.get_by_test_id("card-verification-info")
    await expect(card.get_by_role("heading")).to_contain_text("Thank you for verifying")
    # check can log in and sees onboarding form
    log_in_form = page.locator("#loginForm")
    await expect(page.get_by_label("Email:")).to_have_value(email)
    await page.get_by_label("Password:", exact=True).fill(password)
    await log_in_form.get_by_role("button", name="Log in").click()
    await page.wait_for_url("**/")
    await expect(page.locator("//h1")).to_contain_text("Welcome!")
    # check the tenancy end date provided at signup is reflected on the onboarding form
    await expect(page.get_by_text("You told us your tenancy ends on:")).to_be_visible()
    await expect(page.get_by_test_id("tenancyEndDateInput")).to_have_value(
        one_month_ago.isoformat()
    )


# TODO: test unhappy paths: test validation of sign up fields:
#         - non-TDS prospect
@pytest.mark.asyncio
async def test_sign_up_unhappy_non_tds_prospect(page: Page) -> None:
    today = datetime.today().date()
    one_month_ago = today - timedelta(weeks=4)

    await page.goto(f"{APP_ORIGIN}/")
    await page.get_by_role("button", name="Sign up").click()
    await expect(page.get_by_role("heading", name="Sign up")).to_be_visible()
    # fill out first half of sign-up form (prospect filter)
    filter_prospect_form = page.locator("#filterProspectForm")
    other_provider_radio = page.get_by_role("button", name="A different provider")
    await other_provider_radio.click()
    await page.get_by_test_id("tenancyEndDateInput").fill(one_month_ago.isoformat())
    await filter_prospect_form.get_by_role("button", name="Next").click()
    # check redirected to filter prospect rejection screen
    await page.wait_for_url("**/signup/?step=funnel")
    await expect(page.locator("//h1")).to_contain_text("Sign up")
    await expect(page.get_by_text("Deposit held by other provider")).to_be_visible()
    await expect(
        page.get_by_text(f"Tenancy ended on {one_month_ago.isoformat()}")
    ).to_be_visible()
    await expect(page.locator("//h2")).to_contain_text("It's not you, it's us...")
    start_over_link = page.get_by_test_id("linkToStartOver")
    await expect(start_over_link).to_contain_text("Start over")


# TODO: test unhappy paths: test validation of sign up fields:
#         - out-of-range end date: longer than 3 months ago, over 6 months in the future,
#           within 5 days of TDS dispute window ending.


# TODO: test unhappy path: following expired / invalid verification link


# TODO: in new scenario, pick up where `test_sign_up_happy_path` left off and
#       test onboarding happy path.


@pytest.mark.asyncio
async def test_log_in_happy_path(page: Page) -> None:
    await log_in_user(page, E2EUser.ACTIVE_VERIFIED)
    await expect(page.get_by_test_id("navbarAccountDropdown")).to_be_visible()
    navbar = page.get_by_role("navigation")
    await expect(navbar.get_by_role("button", name="Log in")).to_have_count(0)
    await expect(navbar.get_by_role("button", name="Sign up")).to_have_count(0)


@pytest.mark.asyncio
async def test_protected_routes_next_path_is_forwarded(page: Page) -> None:
    # TODO: make more robust by changing to path other than `/welcome/` once one is
    #       available. Reasoning: `/welcome/` is default for non-onboarded users so
    #       other redirects might interfere with clarity of this test.
    target_path = "/welcome/"
    await page.goto(f"{APP_ORIGIN}{target_path}")
    await expect(page).to_have_url(f"{APP_ORIGIN}/login/?next={target_path}")
    await page.get_by_label("Email:").fill(E2EUser.NEEDS_ONBOARDING.value)
    await page.get_by_label("Password:", exact=True).fill(E2E_USER_PASSWORD)
    await page.locator("#loginForm").get_by_role("button", name="Log in").click()
    await expect(page).to_have_url(f"{APP_ORIGIN}{target_path}")
