from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from api_admin.serializers.sous_phases import SousPhaseSerializer


def _err400_example(name: str, msg: str):
    return OpenApiExample(name, value={"detail": msg}, response_only=True, status_codes=["400"])


schema_sous_phases_admin = extend_schema_view(
    list=extend_schema(
        tags=["Admin - Sous-phases"],
        summary="Lister les sous-phases",
        responses={200: SousPhaseSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Admin - Sous-phases"],
        summary="Détail d’une sous-phase",
        responses={200: SousPhaseSerializer},
    ),
    generer_groupes_phase1=extend_schema(
        tags=["Admin - Sous-phases"],
        summary="Générer les groupes (phase 1) pour une sous-phase",
        description=(
            "Génère les groupes de phase 1 et affecte les équipes pour cette sous-phase.\n\n"
            "Retourne un résumé (pas d’objet complexe)."
        ),
        responses={
            200: OpenApiResponse(
                description="Groupes générés.",
                examples=[
                    OpenApiExample(
                        "Réponse generer-groupes-phase1",
                        value={
                            "created": True,
                            "sous_phase_id": 101,
                            "groupes_crees": 8,
                            "affectations_creees": 32,
                            "detail": "Génération des groupes phase 1 terminée.",
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Erreur métier de génération des groupes.",
                examples=[
                    _err400_example(
                        "Génération impossible", "Pas assez d’équipes pour générer des groupes."
                    )
                ],
            ),
            403: OpenApiResponse(description="Non autorisé (admin requis)."),
        },
    ),
)
