"""
(c) 2024 Alberto Morón Hernández
"""

import re
from datetime import date
from typing import Self

from pydantic import model_validator
from pydantic.networks import validate_email

from depositduck.auth import DepositProvider
from depositduck.forms import BaseForm, BaseFormFields, EmptyValueError


class InvalidEmail(ValueError):
    pass


class PasswordTooShort(ValueError):
    pass


class ConfirmPasswordDoesNotMatch(ValueError):
    pass


class FilterProspectFormFields(BaseFormFields):
    provider_choice: DepositProvider | None
    tenancy_end_date: date | None


class FilterProspectForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return FilterProspectFormFields


class SignupFormFields(BaseFormFields):
    email: str | None
    password: str | None
    confirm_password: str | None

    @model_validator(mode="after")
    def email_is_valid(self) -> Self:
        only_space = re.compile(r"^\s+$")
        if not self.email or self.email == "" or only_space.match(self.email):
            self.add_error("email", EmptyValueError, self.email)
        else:
            try:
                validate_email(self.email)
            except Exception:
                self.add_error("email", InvalidEmail, self.email)
        return self

    # prefer `user_manager.validate_password` to validators here, catching exceptions
    # and using SignupForm's `fields.add_error` to attach these to the form.


class SignupForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return SignupFormFields
