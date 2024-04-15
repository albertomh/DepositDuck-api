"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
async def test_navbar_logged_out(browser_page) -> None:
    page: Page
    async for page in browser_page:
        await page.goto("http://0.0.0.0:8000/")
        navbar = page.get_by_role("navigation")
        await expect(navbar).to_be_visible()
        await expect(navbar.get_by_role("button", name="Log in")).to_be_visible()
        await expect(navbar.get_by_role("button", name="Sign up")).to_be_visible()
        await expect(navbar.get_by_role("img")).to_have_attribute(
            "alt", "The DepositDuck wordmark, with the Sterling duck mascot"
        )

# TODO: add Faker

# TODO: test validation of sign up fields

@pytest.mark.asyncio
async def test_sign_up(browser_page) -> None:
    email = "test@domain.tld"
    password = "MyPassword"
    page: Page
    async for page in browser_page:
        await page.goto("http://0.0.0.0:8000/")
        await page.get_by_role("button", name="Sign up").click()
        await expect(page.get_by_role("heading")).to_contain_text("Sign up")
        sign_up_form = page.locator("#signupForm")
        await page.get_by_label("Email:").fill(email)
        await page.get_by_label("Password:", exact=True).fill(password)
        await page.get_by_label("Confirm password:").fill(password)
        await sign_up_form.get_by_role("button", name="Sign up").click()
        await page.wait_for_url("**/login/?prev=/auth/signup/")
        await expect(page.locator("//h1")).to_contain_text("Log in")
        card = page.locator("#pleaseVerifyCard") 
        await expect(
            card.get_by_role("heading")).to_contain_text("Please verify your email")
        await expect(card.get_by_text("Please follow the link in the email we have sent you to verify your account before logging in")).to_be_visible()
