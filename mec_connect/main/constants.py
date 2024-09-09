from __future__ import annotations

from .choices import GristColumnType

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
