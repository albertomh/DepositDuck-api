"""
(c) 2024 Alberto Morón Hernández
"""

import re
from datetime import date
from typing import Self

from pydantic import (
    PositiveInt,
    model_validator,
)

from depositduck.auth import (
    DatesInWrongOrder,
    TenancyIsTooShort,
    prospect_end_date_is_acceptable,
    prospect_tenancy_dates_are_acceptable,
)
from depositduck.forms import BaseForm, BaseFormFields, EmptyValueError

MINIMUM_DEPOSIT_AMOUNT = 100


class InvalidCharError(ValueError):
    pass


class DepositTooSmall(ValueError):
    pass


class OnboardingFormFields(BaseFormFields):
    name: str | None
    deposit_amount: PositiveInt | None
    tenancy_start_date: date | None
    tenancy_end_date: date | None

    @model_validator(mode="after")
    def name_is_valid(self) -> Self:
        # TODO: limit name to 40 chars
        only_space = re.compile(r"^\s+$")
        if not self.name or self.name == "" or only_space.match(self.name):
            self.add_error("name", EmptyValueError, self.name)
        else:
            # match only Unicode letters, spaces, dash or apostrophe
            re_ok_name = re.compile(r"^[a-zA-ZÀ-ÖÙ-öù-ÿĀ-žḀ-ỿ\s\-\']+$", re.UNICODE)
            if not bool(re_ok_name.match(self.name)):
                self.add_error("name", InvalidCharError, self.name)
            self.name = self.name.strip()
        return self

    @model_validator(mode="after")
    def deposit_amount_is_valid(self) -> Self:
        if not self.deposit_amount or self.deposit_amount == "":
            self.add_error("deposit_amount", EmptyValueError, self.deposit_amount)
        else:
            if self.deposit_amount < MINIMUM_DEPOSIT_AMOUNT:
                self.add_error("deposit_amount", DepositTooSmall, self.deposit_amount)
        return self

    @model_validator(mode="after")
    def end_date_is_acceptable(self) -> Self:
        if self.tenancy_end_date:
            try:
                prospect_end_date_is_acceptable(self.tenancy_end_date)
            except Exception as e:
                self.add_error("tenancy_end_date", type(e), self.tenancy_end_date)
        else:
            self.add_error("tenancy_end_date", EmptyValueError, self.tenancy_end_date)
        return self

    @model_validator(mode="after")
    def start_and_end_are_acceptable(self) -> Self:
        if not self.tenancy_start_date:
            self.add_error("tenancy_start_date", EmptyValueError, self.tenancy_start_date)
        if not self.tenancy_end_date:
            self.add_error("tenancy_end_date", EmptyValueError, self.tenancy_end_date)
        if self.tenancy_start_date and self.tenancy_end_date:
            try:
                prospect_tenancy_dates_are_acceptable(
                    self.tenancy_start_date, self.tenancy_end_date
                )
            except (DatesInWrongOrder, TenancyIsTooShort) as e:
                self.add_error("tenancy_end_date", type(e), self.tenancy_end_date)
        return self


class OnboardingForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return OnboardingFormFields
