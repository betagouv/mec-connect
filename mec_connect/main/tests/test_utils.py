from __future__ import annotations

import pytest
from main.utils import str2bool


def test_str2bool():
    assert str2bool("yes") is True
    assert str2bool("False") is False
    with pytest.raises(ValueError):
        str2bool("invalid")
