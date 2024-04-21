"""
(c) 2024 Alberto Morón Hernández
"""

import os
from enum import StrEnum
from typing import AsyncGenerator

import pytest_asyncio
from playwright.async_api import BrowserType, Page, async_playwright

HEADLESS: bool = os.getenv("E2E_HEADLESS", "true").lower() == "true" or False
SLOW_MO = int(os.getenv("E2E_SLOW_MO", 0))  # delay between steps, in milliseconds


class Browser(StrEnum):
    """
    Used to get a property on an instance of the Playwright class.
    """

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@pytest_asyncio.fixture
async def browser_page() -> AsyncGenerator[Page, None]:
    async with async_playwright() as playwright:
        browser_choice = Browser.CHROMIUM  # TODO: make parameter
        selected_browser: BrowserType = getattr(playwright, browser_choice.value)
        browser = await selected_browser.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        page = await browser.new_page()

        try:
            yield page
        finally:
            await browser.close()
