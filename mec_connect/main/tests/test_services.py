from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from main.models import GristColumn, GritColumnConfig
from main.services import (
    check_table_columns_consistency,
    grist_table_exists,
    map_from_project_payload_object,
    map_from_survey_answer_payload_object,
)

from .factories import GristConfigFactory
from .fixtures import table_columns


@pytest.mark.django_db
def test_map_from_project_payload_object(project_payload_object, default_columns):
    assert map_from_project_payload_object(
        obj=project_payload_object,
        config=GristConfigFactory(create_columns_config=True),
    ) == {
        "name": "Pôle Santé",
        "context": "Le projet consiste à créer un pôle santé",
        "city": "MONNIERES",
        "postal_code": 44690,
        "insee": 44100,
        "department": "Loire-Atlantique",
        "department_code": 44,
        "location": "rue des hirondelles",
        "tags": "tag1,tag2",
    }


@pytest.mark.django_db
def test_map_from_survey_answer_payload_object(survey_answer_payload_object, default_columns):
    assert map_from_survey_answer_payload_object(
        obj=survey_answer_payload_object,
        config=GristConfigFactory(create_columns_config=True),
    ) == {
        "topics": "Commerce rural,Citoyenneté / Participation de la population à la vie locale,"
        "Transition écologique et biodiversité,"
        "Transition énergétique",
        "topics_comment": "Mon commentaire sur les thématiques",
    }


def test_grist_table_exists():
    config = GristConfigFactory.build()
    with patch("main.services.GristApiClient.table_exists", return_value=True) as mock_table_exists:
        assert grist_table_exists(config) is True
        mock_table_exists.assert_called_once_with(table_id=config.table_id)


@pytest.mark.django_db
@patch("main.services.GristApiClient.get_table_columns", Mock(return_value=table_columns))
def test_check_table_columns_consistency(default_columns):
    config = GristConfigFactory(create_columns_config=True)
    assert check_table_columns_consistency(config) is True

    GritColumnConfig.objects.create(
        grist_column=GristColumn.objects.first(),
        grist_config=config,
    )
    assert check_table_columns_consistency(config) is False
