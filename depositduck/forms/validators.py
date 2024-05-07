"""
(c) 2024 Alberto Morón Hernández
"""

import re

from pydantic.networks import validate_email

from depositduck.forms import EmptyValueError


class InvalidEmail(ValueError):
    pass


def is_email_valid(self):
    only_space = re.compile(r"^\s+$")
    if not self.email or self.email == "" or only_space.match(self.email):
        self.add_error("email", EmptyValueError, self.email)
    else:
        try:
            validate_email(self.email)
        except Exception:
            self.add_error("email", InvalidEmail, self.email)
    return self
