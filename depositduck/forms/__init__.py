"""
(c) 2024 Alberto Morón Hernández
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

from pydantic import BaseModel


class EmptyValueError(ValueError):
    pass


class BaseFormFields(BaseModel, ABC):
    # {"field_name": {"CustomException": "user_input", "AnotherExc": "other_input"}}
    errors: dict[str, dict[str, str]] = defaultdict(dict)

    def add_error(self, field_name: str, exception: type[Exception], value: Any) -> None:
        self.errors[field_name][exception.__name__] = value


class BaseForm(ABC):
    def __init__(self, **kwargs) -> None:
        self.user_input: dict = kwargs
        form_fields_class = self.get_form_fields_class()
        self.fields: BaseFormFields = form_fields_class(**self.user_input)

    @abstractmethod
    def get_form_fields_class(self) -> type[BaseFormFields]:
        pass

    def get_classes_for_fields(self) -> dict:
        classes = {}
        for field_name, value in self.user_input.items():
            class_str = ""
            if value is not None:
                errors = self.fields.errors.get(field_name)
                if errors is None:
                    class_str = "is-valid"
                else:
                    class_str = "is-invalid"
                classes[field_name] = class_str
        return classes

    @property
    def can_submit(self) -> bool:
        missing_input = any(v is None for v in self.user_input.values())
        return not missing_input and not bool(self.fields.errors)

    def for_template(self) -> dict:
        fields_export = self.fields.model_dump()
        errors = fields_export.pop("errors")
        # templates should not report errors unless there is user input for that field
        errors = {k: v for k, v in errors.items() if self.user_input.get(k) is not None}

        return {
            "can_submit": self.can_submit,
            "fields": fields_export,
            "errors": errors,
            "user_input": self.user_input,
            "field_classes": self.get_classes_for_fields(),
        }
