"""
Utilities to generate embeddings for use in vector similarity queries.

(c) 2024 Alberto Morón Hernández
"""

import httpx

from depositduck.settings import Settings


async def embed_document(
    settings: Settings, drallam_client: httpx.AsyncClient, doc: str
) -> list[float]:
    if not doc:
        return []

    data = {"model": settings.drallam_embeddings_model, "prompt": doc}
    headers = {"content-type": "application/json"}
    response = await drallam_client.post("/api/embeddings", json=data, headers=headers)
    response_data: dict = response.json()
    return response_data.get("embedding", [])
