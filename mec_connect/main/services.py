from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

from .clients import GristApiClient, RecocoApiClient
from .constants import default_columns_spec
from .models import GristColumn, GristConfig, GritColumnConfig, WebhookEvent

logger = logging.getLogger(__name__)


def update_or_create_project_record(config: GristApiClient, project_id: int, project_data: dict):
    """
    Update a record related to a givent project, in a Grist table,
    or create it if it doesn't exist.
    """

    client = GristApiClient.from_config(config)

    resp = client.get_records(
        table_id=config.table_id,
        filter={"object_id": [project_id]},
    )

    if len(records := resp["records"]):
        client.update_records(
            table_id=config.table_id,
            records={
                records[0]["id"]: project_data,
            },
        )
        return

    client.create_records(
        table_id=config.table_id,
        records=[{"object_id": project_id} | project_data],
    )


def process_project_event(event: WebhookEvent):
    """Process a webhook event related to a project."""

    for grist_config in GristConfig.objects.filter(enabled=True):
        project_id = int(event.object_id)

        project_data = map_from_project_payload_object(
            obj=event.object_data,
            available_keys=grist_config.column_configs.values_list(
                "grist_column__col_id", flat=True
            ),
        )

        update_or_create_project_record(
            config=grist_config, project_id=project_id, project_data=project_data
        )


def process_survey_answer_event(event: WebhookEvent):
    """Process a webhook event related to a survey answer."""

    for grist_config in GristConfig.objects.filter(enabled=True):
        project_id = int(event.object_data.get("project"))

        project_data = map_from_survey_answer_payload_object(
            obj=event.object_data,
            available_keys=grist_config.column_configs.values_list(
                "grist_column__col_id", flat=True
            ),
        )

        update_or_create_project_record(
            config=grist_config, project_id=project_id, project_data=project_data
        )


def fetch_projects_data(config: GristConfig) -> Generator[tuple[int, dict]]:
    """Fetch data related to projects from Recoco API."""

    available_table_headers = config.table_headers

    recoco_client = RecocoApiClient()

    for project in recoco_client.get_projects():
        project_data = map_from_project_payload_object(
            obj=project, available_keys=available_table_headers
        )

        sessions = recoco_client.get_survey_sessions(project_id=project["id"])
        if sessions["count"] > 0:
            answers = recoco_client.get_survey_session_answers(
                session_id=sessions["results"][0]["id"]
            )
            for answer in answers["results"]:
                project_data.update(
                    map_from_survey_answer_payload_object(
                        obj=answer, available_keys=available_table_headers
                    )
                )

        yield project["id"], project_data


def grist_table_exists(config: GristConfig) -> bool:
    """Check if a table exists in Grist."""

    return GristApiClient.from_config(config).table_exists(table_id=config.table_id)


def check_table_columns_consistency(config: GristConfig) -> bool:
    """Check the columns of a table in Grist are consistent with the config."""

    remote_table_columns = GristApiClient.from_config(config).get_table_columns(
        table_id=config.table_id
    )

    return sorted(
        [
            {"id": t["id"], "fields": {k: t["fields"][k] for k in ("label", "type")}}
            for t in remote_table_columns
        ],
        key=lambda x: x["id"],
    ) == sorted(config.table_columns, key=lambda x: x["id"])


def map_from_project_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
    """Map a project payload object to a dictionary with the specified keys."""

    try:
        data = {
            "name": obj["name"],
            "context": obj["description"],
            "city": obj["commune"]["name"],
            "postal_code": int(obj["commune"]["postal"]),
            "insee": int(obj["commune"]["insee"]),
            "department": obj["commune"]["department"]["name"],
            "department_code": int(obj["commune"]["department"]["code"]),
            # FIXME: remove the "if" condition once the API is fixed
            "location": obj["location"] if "location" in obj else None,
            "tags": ",".join(obj["tags"]) if "tags" in obj else None,
        }
    except (KeyError, ValueError) as exc:
        logger.error(f"Error while mapping project #{obj["id"]} payload object: {exc}")
        return {}

    if available_keys is None:
        return data

    return {k: data[k] for k in available_keys if k in data}


def map_from_survey_answer_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
    """Map a survey answer payload object to a dictionary with the specified keys."""

    data = {}

    def _format_choices(_obj):
        return ",".join([c["text"] for c in _obj["choices"]])

    map_question_slugs_columns = {
        "autres-programmes-et-contrats": "dependencies",
        "boussole": "ecological_transition_compass",
        "budget-previsionnel": "budget",
        "calendrier": "calendar",
        "description-de-laction": "action",
        "diagnostic-anct": "diagnostic_anct",
        "indicateurs-de-suivi-et-deval": "evaluation_indicator",
        "maitre-douvrage-2": "ownership",
        "maturite-du-projet": "maturity",
        "partage-a-la-commune": "diagnostic_is_shared",
        "partenaires-2": "partners",
        "perimetre": "perimeter",
        "plan-de-financement-definitif": "final_financing_plan",
        "plan-de-financement-previsionnel": "forecast_financing_plan",
        "procedures-administratives": "administrative_procedures",
        "thematiques-2": "topics",
    }

    match question_slug := obj["question"]["slug"]:
        case "thematiques-2" | "autres-programmes-et-contrats" | "perimetre" | "maturite-du-projet":
            data.update(
                {
                    map_question_slugs_columns[question_slug]: _format_choices(obj),
                    f"{map_question_slugs_columns[question_slug]}_comment": obj["comment"],
                }
            )

        case "budget-previsionnel":
            try:
                data.update({map_question_slugs_columns[question_slug]: float(obj["comment"])})
            except ValueError:
                pass

        case (
            "diagnostic-anct"
            | "calendrier"
            | "plan-de-financement-definitif"
            | "plan-de-financement-previsionnel"
        ):
            data.update(
                {
                    map_question_slugs_columns[question_slug]: obj["comment"],
                    f"{map_question_slugs_columns[question_slug]}_attachment": obj["attachment"],
                }
            )

        case "partage-a-la-commune":
            data.update(
                {
                    map_question_slugs_columns[question_slug]: obj["values"][0] == "Oui",
                }
            )

        case (
            "boussole"
            | "description-de-laction"
            | "indicateurs-de-suivi-et-deval"
            | "maturite-du-projet"
            | "partenaires-2"
            | "procedures-administratives"
            | "plan-de-financement-definitif"
            | "maitre-douvrage-2"
        ):
            data.update({map_question_slugs_columns[question_slug]: obj["comment"]})

        case _:
            logger.info(f"Unhandled question: {obj['question']['text_short']}")

    if available_keys is None:
        return data

    return {k: data[k] for k in available_keys if k in data}


def update_or_create_columns():
    for col_id, col_data in default_columns_spec.items():
        GristColumn.objects.update_or_create(
            col_id=col_id,
            defaults=col_data,
        )


def update_or_create_columns_config(config: GristConfig):
    position = 0
    for col_id in default_columns_spec.keys():
        GritColumnConfig.objects.update_or_create(
            grist_column=GristColumn.objects.get(col_id=col_id),
            grist_config=config,
            defaults={"position": position},
        )
        position += 10
