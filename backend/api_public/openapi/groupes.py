from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from api_public.serializers.groupes import (
    GroupePublicSerializer,
    GroupeDetailPublicSerializer,
)


schema_groupes_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Groupes"],
        summary="Lister les groupes",
        description=(
            "Renvoie la liste des groupes pour une édition.\n\n"
            "- Si `edition` n’est pas fourni : utilise la dernière édition.\n"
            "- Filtres possibles : tournoi, phase globale, branche."
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
                description="Type de phase globale (valeur de `sous_phase.phase_globale.type_phase`).",
            ),
            OpenApiParameter(
                name="branche",
                type=OpenApiTypes.STR,
                required=False,
                description="Branche de sous-phase (ex: CHALLENGE / CONSOLANTE / etc. selon tes choix).",
            ),
        ],
        responses={
            200: GroupePublicSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                name="Exemple liste groupes",
                value=[
                    {
                        "id": 10,
                        "code": "A1",
                        "tournoi_code": "ROOKIE",
                        "branche": "PHASE_1",
                        "equipes": [
                            {"id": 1, "nom": "E1"},
                            {"id": 2, "nom": "E2"},
                            {"id": 3, "nom": "E3"},
                            {"id": 4, "nom": "E4"},
                        ],
                    }
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Groupes"],
        summary="Détail d’un groupe",
        description="Renvoie le détail d’un groupe (incluant la composition).",
        responses={
            200: GroupeDetailPublicSerializer,
        },
        examples=[
            OpenApiExample(
                name="Exemple détail groupe",
                value={
                    "id": 10,
                    "code": "A1",
                    "tournoi_code": "ROOKIE",
                    "branche": "PHASE_1",
                    "equipes": [
                        {"id": 1, "nom": "E1"},
                        {"id": 2, "nom": "E2"},
                        {"id": 3, "nom": "E3"},
                        {"id": 4, "nom": "E4"},
                    ],
                },
                response_only=True,
            )
        ],
    ),
)
