"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from playwright.async_api import Page, expect

from tests.e2e.conftest import APP_ORIGIN, E2EUser, log_in_user


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


# TODO: test navbar logged-in


# TODO: add Faker


@pytest.mark.asyncio
async def test_sign_up_happy_path(page: Page) -> None:
    # email = "test@domain.tld"
    # password = "MyPassword"

    # navigate to sign-up form
    await page.goto(f"{APP_ORIGIN}/")
    await page.get_by_role("button", name="Sign up").click()
    await expect(page.get_by_role("heading", name="Sign up")).to_be_visible()
    # TODO: refactor & reinstate
    # fill out sign-up form
    # sign_up_form = page.locator("#signupForm")
    # await page.get_by_label("Email:").fill(email)
    # await page.get_by_label("Password:", exact=True).fill(password)
    # await page.get_by_label("Confirm password:").fill(password)
    # await sign_up_form.get_by_role("button", name="Sign up").click()
    # await page.wait_for_url("**/login/?prev=/auth/signup/")
    # await expect(page.locator("//h1")).to_contain_text("Log in")
    # # check user prompted to find verification email
    # card = page.get_by_test_id("cardPleaseVerify")
    # await expect(card.get_by_role("heading")).to_contain_text("Pleaseverifyyour email")
    # await expect(
    #     card.get_by_text(
    #     "Please follow the link in the email we have sent you to verify your account "
    #         "before logging in"
    #     )
    # ).to_be_visible()
    # # check verification email and follow verification link
    # mh_email = await get_mailhog_email()
    # assert mh_email.Content.Headers.Subject == ["Your DepositDuck account verification"]
    # soup = BeautifulSoup(mh_email.Content.Body, "html.parser")
    # verify_anchor = soup.find("a", attrs={"data-testid": "link-to-verify"})
    # verify_url = verify_anchor["href"]
    # await page.goto(verify_url)
    # assert "/login" in page.url
    # await expect(page.locator("//h1")).to_contain_text("Log in")
    # card = page.get_by_test_id("card-verification-info")
    # await expect(card.get_by_role("heading")).to_contain_text("Thank you for verifying")
    # # check can log in
    # log_in_form = page.locator("#loginForm")
    # await expect(page.get_by_label("Email:")).to_have_value(email)
    # await page.get_by_label("Password:", exact=True).fill(password)
    # await log_in_form.get_by_role("button", name="Log in").click()
    # await page.wait_for_url("**/")
    # await expect(page.locator("//h1")).to_contain_text("Home")


# TODO: test unhappy paths: test validation of sign up fields


# TODO: test unhappy path: following expired / invalid verification link


@pytest.mark.asyncio
async def test_log_in_happy_path(page: Page) -> None:
    await log_in_user(page, E2EUser.ACTIVE_VERIFIED)
    await expect(page.get_by_test_id("navbarAccountDropdown")).to_be_visible()
    await expect(
        page.locator("#navbar").get_by_role("button", name="Log in")
    ).not_to_be_visible()
    await expect(page.get_by_role("button", name="Sign up")).not_to_be_visible()
