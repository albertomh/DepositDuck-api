"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date

from pydantic import model_validator

from depositduck.auth import DepositProvider
from depositduck.forms import BaseForm, BaseFormFields
from depositduck.forms.validators import is_email_valid


class PasswordTooShort(ValueError):
    pass


class ConfirmPasswordDoesNotMatch(ValueError):
    pass


class FilterProspectFormFields(BaseFormFields):
    provider_choice: DepositProvider | None
    tenancy_end_date: date | None

    # TODO: validate tenancyEndDate min/max range here and call `self.add_error`
    # have generous range that prevents obviously wrong information but
    # still allows dates that will redirect to /signup/?step=funnel


class FilterProspectForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return FilterProspectFormFields


class SignupFormFields(BaseFormFields):
    email: str | None
    password: str | None
    confirm_password: str | None

    _email_is_valid = model_validator(mode="after")(is_email_valid)

    # prefer `user_manager.validate_password` to validators here, catching exceptions
    # and using SignupForm's `fields.add_error` to attach these to the form.


class SignupForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return SignupFormFields
