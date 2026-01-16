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
            "- `categorie` est un alias de `tournoi` (code tournoi).\n"
            "- `status` permet de filtrer selon l’heure courante (A_VENIR / EN_COURS / TERMINE).\n"
            "- `limit` limite le nombre d’éléments retournés."
        ),
        parameters=[
            OpenApiParameter(
                name="edition",
                type=OpenApiTypes.INT,
                required=False,
                description="ID de l’édition. Par défaut : dernière édition.",
            ),
            OpenApiParameter(
                name="categorie",
                type=OpenApiTypes.STR,
                required=False,
                description="Alias de `tournoi` (code tournoi). Ex: ROOKIE, LOISIR, COMPETITEUR.",
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
                description="Type de phase globale. Ex: PHASE_1, PHASE_2, FINALE.",
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
            OpenApiParameter(
                name="equipe",
                type=OpenApiTypes.INT,
                required=False,
                description="ID d’une équipe : matchs où elle est équipe A ou B.",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                required=False,
                description="Filtre temporel : en_cours | a_venir | termines.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                required=False,
                description="Limite le nombre d’éléments retournés.",
            ),
        ],
        responses={200: PlanningPublicSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Exemple planning (liste)",
                value=[
                    {
                        "match_id": 128,
                        "debut": "2026-06-20T14:30:00Z",
                        "terrain": "Terrain 3",
                        "tournoi": "ROOKIE",
                        "phase": "PHASE_1",
                        "groupe": "A1",
                        "equipe_a": "Les Panthers",
                        "equipe_b": "Shooters 91",
                        "score": None,
                        "statut": "A_VENIR",
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
        examples=[
            OpenApiExample(
                name="Exemple planning (détail)",
                value={
                    "match_id": 128,
                    "debut": "2026-06-20T14:30:00Z",
                    "terrain": "Terrain 3",
                    "tournoi": "ROOKIE",
                    "phase": "PHASE_1",
                    "groupe": "A1",
                    "equipe_a": "Les Panthers",
                    "equipe_b": "Shooters 91",
                    "score": None,
                    "statut": "A_VENIR",
                },
                response_only=True,
            ),
        ],
    ),
)
