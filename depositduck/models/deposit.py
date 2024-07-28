"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    computed_field,
)


class TenancyBase(BaseModel):
    deposit_in_p: Annotated[int, Field(strict=True, gt=-1)]
    start_date: date | None = None
    end_date: date
    dispute_window_end: date
    user_id: UUID

    @computed_field
    def deposit_in_gbp(self) -> int:
        return self.deposit_in_p // 100

    @computed_field
    def days_until_dispute_window_end(self) -> int:
        return (self.dispute_window_end - date.today()).days
