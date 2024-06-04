from __future__ import annotations

import pytest


@pytest.fixture
def project_payload_object():
    return {
        "id": 777,
        "name": "Pôle Santé",
        "status": "IN_PROGRESS",
        "inactive_since": None,
        "created_on": "2023-10-10T09:50:32.182591+02:00",
        "updated_on": "2024-05-24T10:54:21.653995+02:00",
        "org_name": "Commune de Bayonne",
        "switchtenders": [
            {
                "username": "sylvie.lacourt@loire-atlantique.gouv.fr",
                "first_name": "sylvie",
                "last_name": "lacourt",
                "email": "sylvie.lacourt@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "pref44"},
                    "organization_position": "CHA",
                },
                "is_active": True,
            },
            {
                "username": "beatrice.charrier@loire-atlantique.gouv.fr",
                "first_name": "Béatrice",
                "last_name": "Charrier",
                "email": "beatrice.charrier@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "PREFECTURE 44"},
                    "organization_position": "Chargée de projets",
                },
                "is_active": True,
            },
            {
                "username": "elodie.le-goff@loire-atlantique.gouv.fr",
                "first_name": "Elodie",
                "last_name": "Le Goff",
                "email": "elodie.le-goff@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "Préfecture 44"},
                    "organization_position": "Chef de bureau",
                },
                "is_active": True,
            },
            {
                "username": "anne.renaudin@caissedesdepots.fr",
                "first_name": "Anne",
                "last_name": "Renaudin",
                "email": "anne.renaudin@caissedesdepots.fr",
                "profile": {
                    "organization": {"name": "Banque des Territoires"},
                    "organization_position": "Chargée de développement territorial",
                },
                "is_active": True,
            },
            {
                "username": "ludivine.perio@loire-atlantique.fr",
                "first_name": "Ludivine",
                "last_name": "Perio",
                "email": "ludivine.perio@loire-atlantique.fr",
                "profile": {
                    "organization": {"name": "Département de Loire-Atlantique"},
                    "organization_position": "Responsable de l'unité developpement territorail",
                },
                "is_active": True,
            },
            {
                "username": "yvan.forgeoux@loire-atlantique.gouv.fr",
                "first_name": "Yvan",
                "last_name": "Forgeoux",
                "email": "yvan.forgeoux@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "DDTM 44"},
                    "organization_position": None,
                },
                "is_active": True,
            },
            {
                "username": "sonia.gourmaud@loire-atlantique.gouv.fr",
                "first_name": "Sonia",
                "last_name": "Gourmaud",
                "email": "sonia.gourmaud@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "DDTM 44"},
                    "organization_position": None,
                },
                "is_active": True,
            },
            {
                "username": "nadia.dik@loire-atlantique.gouv.fr",
                "first_name": "Nadia",
                "last_name": "Dik",
                "email": "nadia.dik@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "DDTM 44"},
                    "organization_position": None,
                },
                "is_active": True,
            },
            {
                "username": "paulina.nawrot@loire-atlantique.gouv.fr",
                "first_name": "Paulina",
                "last_name": "Nawrot",
                "email": "paulina.nawrot@loire-atlantique.gouv.fr",
                "profile": {
                    "organization": {"name": "Préfecture 44"},
                    "organization_position": "Responsable du pôle Soutien aux territoires",
                },
                "is_active": True,
            },
        ],
        "commune": {
            "name": "MONNIERES",
            "insee": "44100",
            "postal": "44690",
            "department": {"name": "Loire-Atlantique", "code": "44"},
            "latitude": 47.1202035218,
            "longitude": -1.34924956417,
        },
        "recommendation_count": 0,
        "public_message_count": 0,
        "private_message_count": 0,
        "topics": [
            {"name": "Financement"},
            {
                "name": "Etudes",
            },
        ],
    }
