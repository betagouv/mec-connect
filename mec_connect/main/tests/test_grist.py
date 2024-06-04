from __future__ import annotations

from main.grist import GristProjectRow


def test_from_event_payload(project_payload_object):
    assert GristProjectRow.from_payload_object(obj=project_payload_object) == GristProjectRow(
        name="Pôle Santé",
        topics="Etudes, Financement",
    )
