from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,

    OpenApiResponse,
    OpenApiExample,
)
from api_admin.schema import REP_400, REP_403, REP_404, TAG_MATCHS, TAG_SCORES
from api_admin.serializers.matchs import MatchSerializer
from api_admin.serializers.planning import SwapPlanningSerializer
from api_admin.serializers.forfaits import ForfaitSerializer


schema_matchs_viewset = extend_schema_view(
    list=extend_schema(
        tags=[TAG_MATCHS],
        summary="Lister les matchs",
        description=(
            "Retourne la liste des matchs.\n\n"
            "Un match est rattaché à une édition, une phase globale, une sous-phase et un groupe.\n"
            "La planification (créneau/terrain) peut être absente tant que le match n'est pas planifié."
        ),
        responses={200: None, 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_MATCHS],
        summary="Lire un match",
        description="Retourne le détail d'un match.",
        responses={200: None, 403: REP_403, 404: REP_404},
    ),
)

schema_generer_feuille = extend_schema(
    tags=[TAG_MATCHS],
    summary="Générer / récupérer la feuille de match",
    description=(
        "Crée la feuille de match si elle n'existe pas, sinon la retourne.\n\n"
        "La feuille porte un `sheet_code` unique destiné à l'impression/identification terrain."
    ),
    responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
)

schema_saisir_score = extend_schema(
    tags=[TAG_SCORES],
    summary="Saisir un score (non validé)",
    description=(
        "Enregistre le score d'un match.\n\n"
        "Le score n'est pas considéré comme officiel tant qu'il n'est pas validé.\n"
        "Le classement est recalculé uniquement lors de la validation."
    ),
    examples=[
        OpenApiExample(
            "Exemple score",
            value={"points_a": 10, "points_b": 8},
            request_only=True,
        )
    ],
    responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
)

schema_valider_score = extend_schema(
    tags=[TAG_SCORES],
    summary="Valider un score (verrouillage + recalcul classement)",
    description=(
        "Valide le score du match :\n"
        "- renseigne valide_le / valide_par\n"
        "- verrouille le score (plus de modifications)\n"
        "- passe le match à TERMINE\n"
        "- déclenche le recalcul automatique du classement du groupe"
    ),
    responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
)

schema_swap_planning = extend_schema(
    tags=["Admin - Matchs"],
    summary="Swap planning entre deux matchs",
    description=(
        "Échange les affectations planning (créneau/terrain) entre deux matchs.\n\n"
        "Endpoint de niveau collection (`/matchs/swap-planning/`)."
    ),
    request=SwapPlanningSerializer,
    responses={
        200: OpenApiResponse(
            description="Swap effectué.",
            examples=[
                OpenApiExample(
                    "Réponse swap-planning",
                    value={
                        "detail": "Swap planning effectué.",
                        "match_a_id": 12,
                        "match_b_id": 34,
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erreur métier (swap impossible).",
            examples=[
                OpenApiExample(
                    "Swap impossible",
                    value={"detail": "Swap impossible pour cette édition/planning."},
                    response_only=True,
                    status_codes=["400"],
                )
            ],
        ),
        403: OpenApiResponse(description="Non autorisé (admin requis)."),
    },
    examples=[
        OpenApiExample(
            "Body swap-planning",
            value={"match_a_id": 12, "match_b_id": 34},
            request_only=True,
        )
    ],
)

schema_forfait = extend_schema(
    tags=["Admin - Matchs"],
    summary="Déclarer un forfait",
    description="Déclare un forfait pour un match (statut fourni dans le body).",
    request=ForfaitSerializer,
    responses={
        200: OpenApiResponse(
            description="Forfait enregistré.",
            examples=[
                OpenApiExample(
                    "Réponse forfait",
                    value={
                        "match_id": 12,
                        "statut_match": "FORFAIT_A",
                        "detail": "Forfait enregistré.",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erreur métier (forfait invalide).",
            examples=[
                OpenApiExample(
                    "Forfait impossible",
                    value={"detail": "Statut forfait invalide pour ce match."},
                    response_only=True,
                    status_codes=["400"],
                )
            ],
        ),
        403: OpenApiResponse(description="Non autorisé (admin requis)."),
    },
    examples=[
        OpenApiExample(
            "Body forfait",
            value={"statut": "FORFAIT_A"},
            request_only=True,
        )
    ],
)