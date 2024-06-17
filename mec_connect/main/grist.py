from __future__ import annotations

import json
import logging
from typing import Any, Self

from httpx import Client, Response

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
    data = {
        "name": obj["name"],
        "context": obj["description"],
    }

    if available_keys is None:
        return data

    return {k: data[k] for k in available_keys if k in data}


def map_from_survey_answer_payload_object(
    obj: dict[str, Any], available_keys: list[str] | None = None
) -> dict[str, Any]:
    data = {}

    # TODO: need a question slug instead of using text_short
    question_slug = obj["question"]["text_short"]

    def _format_choices(_obj):
        return ",".join([c["text"] for c in _obj["choices"]])

    _mapping = {
        "Autres programmes et contrats": "dependencies",
        "Boussole": "ecological_transition_compass",
        "Budget prévisionnel": "budget",
        "Calendrier": "calendar",
        "Description de l'action": "action",
        "Diagnostic ANCT": "diagnostic_anct",
        "Partagé à la commune ?": "diagnostic_is_shared",
        "Indicateurs de suivi et d'éval": "evaluation_indicator",
        "Maturité du projet": "maturity",
        "Partenaires": "partners",
        "Périmètre": "perimeter",
        "Plan de financement prévisionnel": "forecast_financing_plan",
        "Plan de financement définitif": "final_financing_plan",
        "Plan de financement": "financing_plan",
        "Procédures administratives": "administrative_procedures",
        "Thématique(s)": "topics",
        "Maître d'ouvrage": "ownership",
    }

    match question_slug:
        case "Thématique(s)" | "Autres programmes et contrats" | "Périmètre" | "Maturité du projet":
            data.update(
                {
                    _mapping[question_slug]: _format_choices(obj),
                    f"{_mapping[question_slug]}_comment": obj["comment"],
                }
            )

        case "Budget prévisionnel":
            try:
                data.update({_mapping[question_slug]: float(obj["comment"])})
            except ValueError:
                pass

        case (
            "Diagnostic ANCT"
            | "Calendrier"
            | "Plan de financement définitif"
            | "Plan de financement prévisionnel"
        ):
            data.update(
                {
                    _mapping[question_slug]: obj["comment"],
                    f"{_mapping[question_slug]}__attachment": obj["attachment"],
                }
            )

        case "Partagé à la commune ?":
            data.update(
                {
                    _mapping[question_slug]: obj["values"][0] == "Oui",
                }
            )

        case (
            "Boussole"
            | "Description de l'action"
            | "Indicateurs de suivi et d'éval"
            | "Maturité du projet"
            | "Partenaires"
            | "Procédures administratives"
            | "Plan de financement"
            | "Plan de financement définitif"
            | "Maître d'ouvrage"
        ):
            data.update({_mapping[question_slug]: obj["comment"]})

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
