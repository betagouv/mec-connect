from __future__ import annotations

import json
import logging
from typing import Any, Self

from httpx import Client, Response
from main.choices import GristColumnType

from .models import GristConfig

logger = logging.getLogger(__name__)


def raise_on_4xx_5xx(response: Response):
    response.raise_for_status()


class GristApiClient:
    api_key: str
    api_base_url: str
    doc_id: str

    _client: Client

    def __init__(self, api_key: str, api_base_url: str, doc_id: str):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.doc_id = doc_id
        self._client = Client(
            headers=self.headers,
            base_url=self.api_base_url,
            event_hooks={"response": [raise_on_4xx_5xx]},
        )

    @classmethod
    def from_config(cls, config: GristConfig) -> Self:
        return cls(
            api_key=config.api_key,
            api_base_url=config.api_base_url,
            doc_id=config.doc_id,
        )

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_tables(self) -> dict[str, Any]:
        resp = self._client.get(f"docs/{self.doc_id}/tables/")
        return resp.json()

    def create_table(self, table_id: str, columns: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(
            f"docs/{self.doc_id}/tables/",
            json={"tables": [{"id": table_id, "columns": columns}]},
        )
        return resp.json()

    def get_records(self, table_id: str, filter: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.get(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            params={"filter": json.dumps(filter)},
        )
        return resp.json()

    def create_records(self, table_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        resp = self._client.post(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            json={"records": [{"fields": r} for r in records]},
        )
        return resp.json()

    def update_records(self, table_id: str, records: dict[str, dict[str, Any]]) -> dict[str, Any]:
        resp = self._client.patch(
            f"docs/{self.doc_id}/tables/{table_id}/records/",
            json={"records": [{"id": k, "fields": v} for k, v in records.items()]},
        )
        return resp.json()


def map_from_project_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
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
    data = {}

    def _format_choices(_obj):
        return ",".join([c["text"] for c in _obj["choices"]])

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


def grist_table_exists(config: GristConfig) -> bool:
    grist_client = GristApiClient.from_config(config)
    response = grist_client.get_tables()
    for table in response["tables"]:
        if table["id"] == config.table_id:
            return True
    return False


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


default_columns_spec = {
    "object_id": {
        "label": "ID",
        "type": GristColumnType.INTEGER,
    },
    "name": {
        "label": "Nom du projet",
        "type": GristColumnType.TEXT,
    },
    "context": {
        "label": "Contexte",
        "type": GristColumnType.TEXT,
    },
    "tags": {
        "label": "Etiquettes",
        "type": GristColumnType.CHOICE_LIST,
    },
    "topics": {
        "label": "Thématiques",
        "type": GristColumnType.CHOICE_LIST,
    },
    "topics_comment": {
        "label": "Commentaire thématiques",
        "type": GristColumnType.TEXT,
    },
    "city": {
        "label": "Commune",
        "type": GristColumnType.TEXT,
    },
    "postal_code": {
        "label": "Code postal",
        "type": GristColumnType.INTEGER,
    },
    "insee": {
        "label": "Code Insee",
        "type": GristColumnType.INTEGER,
    },
    "department": {
        "label": "Département",
        "type": GristColumnType.TEXT,
    },
    "department_code": {
        "label": "Code département",
        "type": GristColumnType.INTEGER,
    },
    "location": {
        "label": "Lieu",
        "type": GristColumnType.TEXT,
    },
    "perimeter": {
        "label": "Périmètre",
        "type": GristColumnType.CHOICE_LIST,
    },
    "perimeter_comment": {
        "label": "Commentaire périmètre",
        "type": GristColumnType.TEXT,
    },
    "diagnostic_anct": {
        "label": "Diagnostic ANCT",
        "type": GristColumnType.TEXT,
    },
    "diagnostic_anct_attachment": {
        "label": "PJ Diagnostic ANCT",
        "type": GristColumnType.TEXT,
    },
    "diagnostic_is_shared": {
        "label": "Diagnostic partagé",
        "type": GristColumnType.BOOL,
    },
    "maturity": {
        "label": "Niveau de maturité",
        "type": GristColumnType.CHOICE_LIST,
    },
    "maturity__comment": {
        "label": "Commentaire niveau de maturité",
        "type": GristColumnType.TEXT,
    },
    "ownership": {
        "label": "Maitre d'ouvrage",
        "type": GristColumnType.TEXT,
    },
    "action": {
        "label": "Description de l'action",
        "type": GristColumnType.TEXT,
    },
    "partners": {
        "label": "Partenaires",
        "type": GristColumnType.TEXT,
    },
    "budget": {
        "label": "Budget prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "budget_attachment": {
        "label": "PJ budget prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "forecast_financing_plan": {
        "label": "Plan de financement prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "forecast_financing_plan_attachment": {
        "label": "PJ financement prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "final_financing_plan": {
        "label": "Plan de financement définitif",
        "type": GristColumnType.TEXT,
    },
    "final_financing_plan_attachment": {
        "label": "PJ financement définitif",
        "type": GristColumnType.TEXT,
    },
    "calendar": {
        "label": "Calendrier",
        "type": GristColumnType.TEXT,
    },
    "calendar_attachment": {
        "label": "PJ calendrier",
        "type": GristColumnType.TEXT,
    },
    "administrative_procedures": {
        "label": "Procédures administratives",
        "type": GristColumnType.TEXT,
    },
    "dependencies": {
        "label": "Liens avec d'autres programmes et contrats",
        "type": GristColumnType.CHOICE_LIST,
    },
    "dependencies_comment": {
        "label": "Commentaire liens avec d'autres programmes et contrats",
        "type": GristColumnType.TEXT,
    },
    "evaluation_indicator": {
        "label": "Indicateur de suivi et d'évaluation",
        "type": GristColumnType.TEXT,
    },
    "ecological_transition_compass": {
        "label": "Boussole de transition écologique",
        "type": GristColumnType.TEXT,
    },
}
