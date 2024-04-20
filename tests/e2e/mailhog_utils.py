"""
(c) 2024 Alberto Morón Hernández
"""

import httpx
import pytest_asyncio
from pydantic import BaseModel, ConfigDict


class LaxModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class MailHogApiItemContentHeaders(LaxModel):
    To: list[str]
    Subject: list[str]
    From: list[str]


class MailHogApiItemContent(LaxModel):
    Headers: MailHogApiItemContentHeaders
    Body: str
    Size: int


class MailHogApiItem(LaxModel):
    ID: str
    From: dict
    To: list[dict]
    Content: MailHogApiItemContent


class MailHogApiResponse(BaseModel):
    total: int
    count: int
    start: int
    items: list[MailHogApiItem]


async def get_mailhog_api_client() -> httpx.AsyncClient:
    base_url = "http://0.0.0.0:8025/api"
    client = httpx.AsyncClient(base_url=base_url)
    return client


async def get_mailhog_email() -> MailHogApiItem:
    async with await get_mailhog_api_client() as mailhog_api:
        raw = await mailhog_api.get("/v2/messages")
        res = MailHogApiResponse(**raw.json())

        if res.total == 0:
            raise ValueError("zero emails in MailHog during e2e test")
        if res.total > 1:
            raise ValueError("more than one email in MailHog during e2e test")

        return res.items[0]


@pytest_asyncio.fixture(autouse=True)
async def wipe_mailhog() -> None:
    client = await get_mailhog_api_client()
    async with client as mailhog_api:
        await mailhog_api.delete("/v1/messages")
