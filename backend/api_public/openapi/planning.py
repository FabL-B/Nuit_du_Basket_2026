from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from api_public.serializers.planning import PlanningPublicSerializer


schema_planning_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Planning"],
        summary="Lister le planning",
        description=(
            "Renvoie la liste des matchs planifiés (créneau + terrain).\n\n"
            "- Si `edition` n’est pas fourni : utilise la dernière édition (par `date_evenement`).\n"
            "- Filtres possibles : `tournoi`/`tournoi_code`, `phase`, `groupe`, `terrain`."
        ),
        parameters=[
            OpenApiParameter(
                name="edition",
                type=OpenApiTypes.INT,
                required=False,
                description="ID de l’édition. Par défaut : dernière édition.",
            ),
            OpenApiParameter(
                name="tournoi",
                type=OpenApiTypes.STR,
                required=False,
                description="Code du tournoi (alias de `tournoi_code`). Ex: ROOKIE, LOISIR, COMPETITEUR.",
            ),
            OpenApiParameter(
                name="tournoi_code",
                type=OpenApiTypes.STR,
                required=False,
                description="Code du tournoi. Ex: ROOKIE, LOISIR, COMPETITEUR.",
            ),
            OpenApiParameter(
                name="phase",
                type=OpenApiTypes.STR,
                required=False,
                description="Type de phase globale (valeur de `phase_globale.type_phase`).",
            ),
            OpenApiParameter(
                name="groupe",
                type=OpenApiTypes.INT,
                required=False,
                description="ID du groupe.",
            ),
            OpenApiParameter(
                name="terrain",
                type=OpenApiTypes.INT,
                required=False,
                description="ID du terrain.",
            ),
        ],
        responses={
            200: PlanningPublicSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                name="Exemple planning (liste)",
                value=[
                    {
                        "id": 123,
                        "debut": "2026-06-20T14:00:00Z",
                        "terrain": {"id": 1, "nom": "T1"},
                        "tournoi": {"code": "ROOKIE", "nom": "Rookie"},
                        "phase": "PHASE_1",
                        "groupe": {"id": 10, "nom": "A1"},
                        "equipe_a": {"id": 1, "nom": "E1"},
                        "equipe_b": {"id": 2, "nom": "E2"},
                        "score": None,
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Planning"],
        summary="Détail d’un match planifié",
        description="Renvoie le détail d’un match (mêmes champs que la liste).",
        responses={200: PlanningPublicSerializer},
    ),
)
