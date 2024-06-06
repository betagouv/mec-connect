from __future__ import annotations

from django.core.management.base import BaseCommand
from main.choices import GristColumnType
from main.models import GristColumn

columns_spec = {
    "object_id": {
        "label": "ID",
        "type": GristColumnType.TEXT,
    },
    "name": {
        "label": "Nom du projet",
        "type": GristColumnType.TEXT,
    },
    "context": {
        "label": "Contexte",
        "type": GristColumnType.TEXT,
    },
    "topics": {
        "label": "Thématiques",
        "type": GristColumnType.TEXT,
    },
    "additions": {
        "label": "Compléments",
        "type": GristColumnType.TEXT,
    },
    "details": {
        "label": "Si autre, précisez",
        "type": GristColumnType.TEXT,
    },
    "perimeter": {
        "label": "Périmètre",
        "type": GristColumnType.TEXT,
    },
    "diagnostic_anct": {
        "label": "Diagnostic ANCT",
        "type": GristColumnType.TEXT,
    },
    "attachment": {
        "label": "Pièces jointes",
        "type": GristColumnType.TEXT,
    },
    "diagnostic_is_shared": {
        "label": "Le diagnostic a-t-il été partagé à la commune ?",
        "type": GristColumnType.BOOLEAN,
    },
    "maturity": {
        "label": "Niveau de maturité",
        "type": GristColumnType.TEXT,
    },
    "ownership": {
        "label": "Maître d'ouvrage",
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
        "type": GristColumnType.INTEGER,
    },
    "budget_attachment": {
        "label": "PJ Budget prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "final_budget": {
        "label": "Budget définitif",
        "type": GristColumnType.INTEGER,
    },
    "final_budget_attachment": {
        "label": "PJ Budget définitif",
        "type": GristColumnType.TEXT,
    },
    "forecast_financing_plan": {
        "label": "Plan de financement prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "forecast_financing_plan_attachment": {
        "label": "PJ Financement prévisionnel",
        "type": GristColumnType.TEXT,
    },
    "final_financing_plan": {
        "label": "Plan de financement définitif",
        "type": GristColumnType.TEXT,
    },
    "final_financing_plan_attachment": {
        "label": "PJ Financement définitif",
        "type": GristColumnType.TEXT,
    },
    "calendar": {
        "label": "Calendrier",
        "type": GristColumnType.TEXT,
    },
    "administrative_procedures": {
        "label": "Procédures administratives",
        "type": GristColumnType.TEXT,
    },
    "dependencies": {
        "label": "Liens avec d'autres programmes et contrats",
        "type": GristColumnType.TEXT,
    },
    "evaluation_indicator": {
        "label": "Indicateur de suivi et d'évaluation",
        "type": GristColumnType.TEXT,
    },
    "ecological_transition_compass": {
        "label": "Boussole de transition ecologique",
        "type": GristColumnType.TEXT,
    },
    "verdict": {
        "label": "Verdict",
        "type": GristColumnType.TEXT,
    },
    "grant_amount": {
        "label": "Montant de subvention",
        "type": GristColumnType.INTEGER,
    },
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        position = 0
        for col_id, col_data in columns_spec.items():
            self.stdout.write(f"Creating column {col_id}")
            GristColumn.objects.update_or_create(
                col_id=col_id,
                defaults=col_data | {"position": position},
            )
            position += 1
