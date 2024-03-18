"""
(c) 2024 Alberto Morón Hernández
"""

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel


async def init_db(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
