"""
(c) 2024 Alberto Morón Hernández
"""

from abc import ABC, abstractmethod
from collections import defaultdict

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails


class BaseForm(ABC):
    def __init__(self, **kwargs) -> None:
        self.can_submit_form = False
        self.errors: list[ErrorDetails] = []
        self.field_values: dict = kwargs
        self.initialize_fields()

    @abstractmethod
    def get_form_fields_class(self) -> type[BaseModel]:
        pass

    def initialize_fields(self) -> None:
        try:
            form_fields_class = self.get_form_fields_class()
            form: BaseModel = form_fields_class(**self.field_values)
            self.field_values = form.model_dump()
        except ValidationError as e:
            self.errors = e.errors()

    def get_errors_for_frontend(self) -> dict:
        errors: dict[str, dict[str, str]] = defaultdict(dict)
        if self.errors:
            for error in self.errors:
                loc = str(error["loc"][0])
                if self.field_values.get(loc) is not None:
                    error_cls = type(error["ctx"]["error"]).__name__
                    errors[loc][error_cls] = error["input"]
        return errors

    def get_classes_for_fields(self) -> dict:
        classes = {}
        for field_name, value in self.field_values.items():
            class_str = ""
            if value is not None:
                errors = self.get_errors_for_frontend().get(field_name)
                if errors is None:
                    class_str = "is-valid"
                else:
                    class_str = "is-invalid"
                classes[field_name] = class_str
        return classes

    def for_template(self) -> dict:
        return {
            "can_submit": self.can_submit_form,
            "values": self.field_values,
            "field_classes": self.get_classes_for_fields(),
            "errors": self.get_errors_for_frontend(),
        }
