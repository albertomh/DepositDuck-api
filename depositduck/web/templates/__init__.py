"""
(c) 2024 Alberto Morón Hernández
"""

from enum import Enum


# TODO: remove and refactor all uses to use Alpine.js
class BootstrapClasses(str, Enum):
    FORM_CONTROL = "form-control"
    IS_VALID = "is-valid"
    IS_INVALID = "is-invalid"
