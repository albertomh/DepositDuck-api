"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, PositiveInt


class TenancyBase(BaseModel):
    deposit_in_p: PositiveInt
    start_date: datetime | None = None
    end_date: datetime
    user_id: UUID
