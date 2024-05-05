"""
(c) 2024 Alberto Morón Hernández
"""

import re

from pydantic import BaseModel, PositiveInt, field_validator

from depositduck.forms import BaseForm

MINIMUM_DEPOSIT_AMOUNT = 100


class EmptyStringError(ValueError):
    pass


class InvalidCharError(ValueError):
    pass


class DepositTooSmall(ValueError):
    pass


class OnboardingFormFields(BaseModel):
    name: str | None
    deposit_amount: PositiveInt | None
    # tenancy_start_date: date
    # tenancy_end_date: date

    @field_validator("name")
    @classmethod
    def name_is_valid(cls, v: str) -> str:
        if not v or v == "":
            raise EmptyStringError()
        # match only Unicode letters, spaces, dash or apostrophe
        pattern = re.compile(r"^[a-zA-ZÀ-ÖÙ-öù-ÿĀ-žḀ-ỿ\s\-\']+$", re.UNICODE)
        if not bool(pattern.match(v)):
            raise InvalidCharError()
        return v.strip()

    @field_validator("deposit_amount")
    @classmethod
    def deposit_amount_is_valid(cls, v: int) -> int:
        if not v or v == "":
            raise EmptyStringError()
        if v < MINIMUM_DEPOSIT_AMOUNT:
            raise DepositTooSmall()
        return v


class OnboardingForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseModel]:
        return OnboardingFormFields
