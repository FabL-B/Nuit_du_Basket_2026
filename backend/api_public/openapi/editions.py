from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
)

from api_public.serializers.editions import EditionPublicSerializer


schema_editions_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Metadata"],
        summary="Lister les éditions",
        description=(
            "Renvoie la liste de toutes les éditions.\n\n"
            "Les éditions sont triées par date d’événement décroissante "
            "(édition la plus récente en premier)."
        ),
        responses={
            200: EditionPublicSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                name="Exemple liste éditions",
                value=[
                    {
                        "id": 3,
                        "nom": "Nuit du Basket 2026",
                        "date_evenement": "2026-06-20",
                        "heure_debut": "14:00:00",
                        "duree_creneau_minutes": 15,
                    }
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Metadata"],
        summary="Détail d’une édition",
        description="Renvoie le détail d’une édition.",
        responses={
            200: EditionPublicSerializer,
        },
    ),
)
