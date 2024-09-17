from __future__ import annotations

import pytest
from main.choices import GristColumnType
from main.models import GristColumnFilter
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from .factories import GristColumnFactory, GristConfigFactory


class GristColumnFilterTests(ParametrizedTestCase):
    @parametrize(
        "column_type, filter_value, exception_raised",
        [
            param(GristColumnType.INTEGER, "dummy value", True, id="integer_cast_fail"),
            param(GristColumnType.INTEGER, "123", False, id="integer_cast_success"),
            param(GristColumnType.BOOL, "dummy value", True, id="bool_cast_fail"),
            param(GristColumnType.BOOL, "true", False, id="bool_cast_success"),
        ],
    )
    @pytest.mark.django_db
    def test_filter_value(self, filter_value, column_type, exception_raised):
        filter_instance = GristColumnFilter(
            grist_config=GristConfigFactory(),
            grist_column=GristColumnFactory(type=column_type),
            filter_value=filter_value,
        )
        if exception_raised:
            with pytest.raises(ValueError):
                filter_instance.save()
        else:
            filter_instance.save()
            assert filter_instance.pk is not None
