from __future__ import annotations

import pytest
from main.choices import FilterOperator, GristColumnType
from main.models import GristColumnFilter
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from .factories import GristColumnFactory, GristColumnFilterFactory, GristConfigFactory


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

    @parametrize(
        "column_type, filter_value, value, filter_operator, expected_result",
        [
            param(
                GristColumnType.INTEGER,
                "dummy value",
                "1",
                FilterOperator.EQUAL,
                False,
                id="invalid_value",
            ),
            param(
                GristColumnType.INTEGER,
                "1",
                "dummy value",
                FilterOperator.EQUAL,
                False,
                id="invalid_filter_value",
            ),
            param(
                GristColumnType.TEXT,
                "value",
                "value",
                FilterOperator.EQUAL,
                True,
                id="equal",
            ),
            param(
                GristColumnType.TEXT,
                "value",
                "VALUE",
                FilterOperator.EQUAL,
                False,
                id="not_equal",
            ),
            param(
                GristColumnType.TEXT,
                "value",
                "VALUE",
                FilterOperator.I_EQUAL,
                True,
                id="iequal",
            ),
            param(
                GristColumnType.TEXT,
                "value 2",
                "VALUE",
                FilterOperator.I_EQUAL,
                False,
                id="not_iequal",
            ),
            param(
                GristColumnType.TEXT,
                "deux",
                "un,deux,trois",
                FilterOperator.CONTAINS,
                True,
                id="contains",
            ),
            param(
                GristColumnType.TEXT,
                "quatre",
                "un,deux,trois",
                FilterOperator.CONTAINS,
                False,
                id="not_contains",
            ),
            param(
                GristColumnType.TEXT,
                "deux",
                "UN,DEUX,TROIS",
                FilterOperator.I_CONTAINS,
                True,
                id="icontains",
            ),
            param(
                GristColumnType.TEXT,
                "quatre",
                "UN,DEUX,TROIS",
                FilterOperator.I_CONTAINS,
                False,
                id="not_icontains",
            ),
        ],
    )
    @pytest.mark.django_db
    def test_check_value(self, column_type, value, filter_value, filter_operator, expected_result):
        filter: GristColumnFilter = GristColumnFilterFactory.build(
            grist_column__type=column_type,
            filter_value=filter_value,
            filter_operator=filter_operator,
        )
        assert filter.check_value(value) == expected_result
