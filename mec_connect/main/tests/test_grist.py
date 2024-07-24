from __future__ import annotations

from main.grist import (
    map_from_project_payload_object,
    map_from_survey_answer_payload_object,
)


def test_map_from_project_payload_object(project_payload_object):
    assert map_from_project_payload_object(obj=project_payload_object) == {
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


def test_map_from_survey_answer_payload_object(survey_answer_payload_object):
    assert map_from_survey_answer_payload_object(obj=survey_answer_payload_object) == {
        "topics": "Commerce rural,Citoyenneté / Participation de la population à la vie locale,"
        "Transition écologique et biodiversité,"
        "Transition énergétique",
        "topics_comment": "Mon commentaire sur les thématiques",
    }
