"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from bs4 import BeautifulSoup
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


# TODO: test navbar logged-in

# TODO: test log in with existing user (must first add e2e db fixtures)

# TODO: add Faker


@pytest.mark.asyncio
async def test_sign_up_happy_path(browser_page: Page) -> None:
    email = "test@domain.tld"
    password = "MyPassword"

    # navigate to sign-up form
    await browser_page.goto("http://0.0.0.0:8000/")
    await browser_page.get_by_role("button", name="Sign up").click()
    await expect(browser_page.get_by_role("heading")).to_contain_text("Sign up")
    # fill out sign-up form
    sign_up_form = browser_page.locator("#signupForm")
    await browser_page.get_by_label("Email:").fill(email)
    await browser_page.get_by_label("Password:", exact=True).fill(password)
    await browser_page.get_by_label("Confirm password:").fill(password)
    await sign_up_form.get_by_role("button", name="Sign up").click()
    await browser_page.wait_for_url("**/login/?prev=/auth/signup/")
    await expect(browser_page.locator("//h1")).to_contain_text("Log in")
    # check user prompted to find verification email
    card = browser_page.get_by_test_id("card-please-verify")
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
    verify_anchor = soup.find("a", attrs={"data-testid": "link-to-verify"})
    verify_url = verify_anchor["href"]
    await browser_page.goto(verify_url)
    assert "/login" in browser_page.url
    await expect(browser_page.locator("//h1")).to_contain_text("Log in")
    card = browser_page.get_by_test_id("card-verification-info")
    await expect(card.get_by_role("heading")).to_contain_text("Thank you for verifying")
    # check can log in
    log_in_form = browser_page.locator("#loginForm")
    await expect(browser_page.get_by_label("Email:")).to_have_value(email)
    await browser_page.get_by_label("Password:", exact=True).fill(password)
    await log_in_form.get_by_role("button", name="Log in").click()
    await browser_page.wait_for_url("**/")
    await expect(browser_page.locator("//h1")).to_contain_text("Home")


# TODO: test unhappy paths: test validation of sign up fields


# TODO: test unhappy path: following expired / invalid verification link
