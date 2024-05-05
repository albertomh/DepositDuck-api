"""
(c) 2024 Alberto Morón Hernández
"""

from pydantic import (
    EmailStr,
)

from depositduck.forms import BaseForm, BaseFormFields


class VerificationLinkExpired(Exception):
    pass


class LoginBadCredentials(ValueError):
    pass


class UserNotVerified(ValueError):
    pass


class LoginFormFields(BaseFormFields):
    username: EmailStr | None
    password: str | None


class LoginForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return LoginFormFields
