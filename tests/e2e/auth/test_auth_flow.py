"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from playwright.async_api import Page, expect

from tests.e2e.mailhog_utils import get_mailhog_email


@pytest.mark.asyncio
async def test_navbar_logged_out(browser_page: Page) -> None:
    await browser_page.goto("http://0.0.0.0:8000/")
    navbar = browser_page.get_by_role("navigation")
    await expect(navbar).to_be_visible()
    await expect(navbar.get_by_role("button", name="Log in")).to_be_visible()
    await expect(navbar.get_by_role("button", name="Sign up")).to_be_visible()
    await expect(navbar.get_by_role("img")).to_have_attribute(
        "alt", "The DepositDuck wordmark, with the Sterling duck mascot"
    )


# TODO: add Faker

# TODO: test validation of sign up fields


@pytest.mark.asyncio
async def test_sign_up_happy_path(browser_page: Page) -> None:
    email = "test@domain.tld"
    password = "MyPassword"

    # navigate to sign-up form
    await browser_page.goto("http://0.0.0.0:8000/")
    await browser_page.get_by_role("button", name="Sign up").click()
    await expect(browser_page.get_by_role("heading")).to_contain_text("Sign up")
    # fill out form
    sign_up_form = browser_page.locator("#signupForm")
    await browser_page.get_by_label("Email:").fill(email)
    await browser_page.get_by_label("Password:", exact=True).fill(password)
    await browser_page.get_by_label("Confirm password:").fill(password)
    await sign_up_form.get_by_role("button", name="Sign up").click()
    await browser_page.wait_for_url("**/login/?prev=/auth/signup/")
    await expect(browser_page.locator("//h1")).to_contain_text("Log in")
    # check email verification prompts
    card = browser_page.get_by_test_id("card-please-verify")
    await expect(card.get_by_role("heading")).to_contain_text("Please verify your email")
    await expect(
        card.get_by_text(
            "Please follow the link in the email we have sent you to verify your account "
            "before logging in"
        )
    ).to_be_visible()
    # check verification email itself and extract verification link
    mh_email = await get_mailhog_email()
    assert mh_email.Content.Headers.Subject == ["Your DepositDuck account verification"]

    # TODO: install bs4 and parse HTML
