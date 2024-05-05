"""
(c) 2024 Alberto Morón Hernández
"""

import re

from pydantic import BaseModel, field_validator

from depositduck.forms import BaseForm


class EmptyStringError(ValueError):
    pass


class InvalidCharError(ValueError):
    pass


class OnboardingFormFields(BaseModel):
    name: str | None
    # deposit_amount: PositiveInt
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
        return re.sub(r"\s+", " ", v).strip()


class OnboardingForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseModel]:
        return OnboardingFormFields
