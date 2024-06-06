from __future__ import annotations

from main.grist import (
    map_from_project_payload_object,
    map_from_survey_answer_payload_object,
)


def test_map_from_project_payload_object(project_payload_object):
    assert map_from_project_payload_object(obj=project_payload_object) == {"name": "Pôle Santé"}


def test_map_from_survey_answer_payload_object(survey_answer_payload_object):
    assert map_from_survey_answer_payload_object(obj=survey_answer_payload_object) == {
        "topics": "Commerce rural,Citoyenneté / Participation de la population à la vie locale,"
        "Transition écologique et biodiversité,"
        "Transition énergétique"
    }
