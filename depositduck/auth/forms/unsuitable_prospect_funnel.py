"""
(c) 2024 Alberto Morón Hernández
"""

import re
from typing import Self

from pydantic import model_validator

from depositduck.forms import BaseForm, BaseFormFields, EmptyValueError
from depositduck.forms.validators import is_email_valid


class UnsuitableProspectFormFields(BaseFormFields):
    email: str | None
    provider_name: str | None

    _email_is_valid = model_validator(mode="after")(is_email_valid)

    @model_validator(mode="after")
    def provider_name_is_valid(self) -> Self:
        only_space = re.compile(r"^\s+$")
        if (
            not self.provider_name
            or self.provider_name == ""
            or only_space.match(self.provider_name)
        ):
            self.add_error("provider_name", EmptyValueError, self.provider_name)
        return self


class UnsuitableProspectForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return UnsuitableProspectFormFields
