from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse,
    OpenApiExample,
)

from api_admin.schema import REP_400, REP_403, REP_404, TAG_GROUPES
from api_admin.serializers.groupes import GroupeSerializer


schema_groupes_viewset = extend_schema_view(
    list=extend_schema(
        tags=[TAG_GROUPES],
        summary="Lister les groupes",
        description=(
            "Retourne la liste des groupes.\n\n"
            "Usage typique : filtrer par sous_phase pour afficher uniquement les groupes d'une sous-phase."
        ),
        parameters=[
            OpenApiParameter(
                "phase_globale", OpenApiTypes.INT, required=False, description="ID phase globale"
            ),
            OpenApiParameter(
                "sous_phase", OpenApiTypes.INT, required=False, description="ID sous-phase"
            ),
            OpenApiParameter("tournoi", OpenApiTypes.INT, required=False, description="ID tournoi"),
        ],
        responses={200: GroupeSerializer(many=True), 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_GROUPES],
        summary="Lire un groupe",
        description="Retourne le détail d'un groupe.",
        responses={200: GroupeSerializer, 403: REP_403, 404: REP_404},
    ),
    create=extend_schema(
        tags=["Admin - Groupes"],
        summary="Créer un groupe",
        responses={201: GroupeSerializer},
    ),
    update=extend_schema(
        tags=["Admin - Groupes"],
        summary="Mettre à jour un groupe",
        responses={200: GroupeSerializer},
    ),
    partial_update=extend_schema(
        tags=["Admin - Groupes"],
        summary="Mettre à jour partiellement un groupe",
        responses={200: GroupeSerializer},
    ),
    destroy=extend_schema(
        tags=["Admin - Groupes"],
        summary="Supprimer un groupe",
        responses={204: OpenApiResponse(description="Supprimé.")},
    ),
)

schema_swap_equipes = extend_schema(
    tags=[TAG_GROUPES],
    summary="Interchanger deux équipes entre deux groupes",
    description=(
        "Interchange deux équipes entre deux groupes.\n\n"
        "Contraintes strictes :\n"
        "- les deux groupes doivent être dans la même sous-phase\n"
        "- les équipes doivent appartenir à la même édition et au même tournoi\n"
        "- opération atomique (transaction)\n\n"
        "Usage : ajustement manuel après création des groupes."
    ),
    examples=[
        OpenApiExample(
            "Exemple swap",
            value={
                "groupe_a_id": 1,
                "equipe_a_id": 10,
                "groupe_b_id": 2,
                "equipe_b_id": 14,
            },
            request_only=True,
        )
    ],
    responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
)
