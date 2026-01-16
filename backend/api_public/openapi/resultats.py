from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from api_public.serializers.resultats import ResultatPublicSerializer


schema_resultats_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Résultats"],
        summary="Lister les résultats",
        description=(
            "Renvoie les matchs **terminés et validés** "
            "(match planifié + score présent + `score.valide_le` non nul).\n\n"
            "- Si `edition` n’est pas fourni : utilise la dernière édition.\n"
            "- `categorie` est un alias de `tournoi` (code tournoi).\n"
            "- Filtres possibles : tournoi, phase, groupe, équipe.\n"
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
                name="equipe",
                type=OpenApiTypes.INT,
                required=False,
                description="ID d’une équipe : résultats où elle est équipe A ou B.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                required=False,
                description="Limite le nombre d’éléments retournés.",
            ),
        ],
        responses={200: ResultatPublicSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Exemple résultats (liste)",
                value=[
                    {
                        "match_id": 456,
                        "debut": "2026-06-20T14:00:00Z",
                        "terrain": "Terrain 1",
                        "tournoi": "ROOKIE",
                        "phase": "PHASE_1",
                        "groupe": "A1",
                        "equipe_a": "E1",
                        "equipe_b": "E2",
                        "score": {"points_a": 15, "points_b": 12},
                        "score_valide_le": "2026-06-20T14:12:00Z",
                    }
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Résultats"],
        summary="Détail d’un match validé",
        description="Renvoie le détail d’un match validé (score présent et validé).",
        responses={200: ResultatPublicSerializer},
        examples=[
            OpenApiExample(
                name="Exemple résultat (détail)",
                value={
                    "match_id": 456,
                    "debut": "2026-06-20T14:00:00Z",
                    "terrain": "Terrain 1",
                    "tournoi": "ROOKIE",
                    "phase": "PHASE_1",
                    "groupe": "A1",
                    "equipe_a": "E1",
                    "equipe_b": "E2",
                    "score": {"points_a": 15, "points_b": 12},
                    "score_valide_le": "2026-06-20T14:12:00Z",
                },
                response_only=True,
            )
        ],
    ),
)
