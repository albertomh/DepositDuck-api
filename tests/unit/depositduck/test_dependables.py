"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.dependables import get_settings
from depositduck.settings import Settings


def test_get_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)


@pytest.mark.skip(reason="TODO: stub")
def test_get_templates():
    pass
