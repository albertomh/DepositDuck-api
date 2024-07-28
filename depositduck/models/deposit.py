"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, PositiveInt


class TenancyBase(BaseModel):
    deposit_in_p: PositiveInt
    start_date: date | None = None
    end_date: date
    dispute_deadline: date
    user_id: UUID
