"""
(c) 2024 Alberto Morón Hernández
"""

import re
from datetime import date
from typing import Self

from pydantic import (
    EmailStr,
    model_validator,
)

from depositduck.auth import DepositProvider
from depositduck.forms import BaseForm, BaseFormFields, EmptyValueError


class FilterProspectFormFields(BaseFormFields):
    provider_choice: DepositProvider | None
    tenancy_end_date: date | None


class FilterProspectForm(BaseForm):
    def get_form_fields_class(self) -> type[BaseFormFields]:
        return FilterProspectFormFields
