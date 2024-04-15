"""
(c) 2024 Alberto Morón Hernández
"""

from enum import StrEnum
from typing import AsyncGenerator

import pytest
from playwright.async_api import BrowserType, Page, async_playwright


class Browser(StrEnum):
    """
    Used to get a property on an instance of the Playwright class.
    """

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@pytest.fixture
async def browser_page() -> AsyncGenerator[Page, None]:
    async with async_playwright() as playwright:
        browser_choice = Browser.CHROMIUM  # TODO: make parameter
        selected_browser: BrowserType = getattr(playwright, browser_choice.value)
        browser = await selected_browser.launch()
        page = await browser.new_page()

        try:
            yield page
        finally:
            await browser.close()
