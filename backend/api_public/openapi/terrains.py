from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from api_public.serializers.terrains import TerrainPublicSerializer


schema_terrains_public = extend_schema_view(
    list=extend_schema(
        tags=["Public - Metadata"],
        summary="Lister les terrains",
        description=(
            "Renvoie la liste des terrains pour une édition.\n\n"
            "- Si `edition` n’est pas fourni : utilise la dernière édition.\n"
            "- Par défaut, seuls les terrains actifs sont retournés.\n"
            "- Le paramètre `actif` permet d’inclure les terrains inactifs."
        ),
        parameters=[
            OpenApiParameter(
                name="edition",
                type=OpenApiTypes.INT,
                required=False,
                description="ID de l’édition. Par défaut : dernière édition.",
            ),
            OpenApiParameter(
                name="actif",
                type=OpenApiTypes.BOOL,
                required=False,
                description=(
                    "Filtre sur l’état actif du terrain.\n"
                    "- true / 1 (par défaut) : terrains actifs uniquement\n"
                    "- false / 0 : inclut les terrains inactifs"
                ),
            ),
        ],
        responses={
            200: TerrainPublicSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                name="Exemple liste terrains",
                value=[
                    {
                        "id": 1,
                        "nom": "Terrain 1",
                        "ordre": 1,
                        "est_actif": True,
                        "edition": {
                            "id": 3,
                            "nom": "Nuit du Basket 2026",
                        },
                    }
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Public - Metadata"],
        summary="Détail d’un terrain",
        description="Renvoie le détail d’un terrain.",
        responses={
            200: TerrainPublicSerializer,
        },
    ),
)
