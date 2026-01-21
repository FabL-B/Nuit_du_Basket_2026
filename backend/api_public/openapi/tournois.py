from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from api_public.serializers.tournois import TournoiPublicSerializer


schema_tournois_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Tournois"],
        summary="Lister les tournois",
        description=(
            "Renvoie la liste des tournois pour une édition.\n\n"
            "- Si `edition` n’est pas fourni : utilise la dernière édition.\n"
            "- Les tournois sont triés par code."
        ),
        parameters=[
            OpenApiParameter(
                name="edition",
                type=OpenApiTypes.INT,
                required=False,
                description="ID de l’édition. Par défaut : dernière édition.",
            ),
        ],
        responses={
            200: TournoiPublicSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                name="Exemple liste tournois",
                value=[
                    {
                        "id": 1,
                        "code": "ROOKIE",
                        "nom": "Rookie",
                        "edition": {"id": 3, "nom": "NDB 2026"},
                    },
                    {
                        "id": 2,
                        "code": "LOISIR",
                        "nom": "Loisir",
                        "edition": {"id": 3, "nom": "NDB 2026"},
                    },
                    {
                        "id": 3,
                        "code": "COMPETITEUR",
                        "nom": "Compétiteur",
                        "edition": {"id": 3, "nom": "NDB 2026"},
                    },
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Tournois"],
        summary="Détail d’un tournoi",
        description="Renvoie le détail d’un tournoi.",
        responses={200: TournoiPublicSerializer},
    ),
)
