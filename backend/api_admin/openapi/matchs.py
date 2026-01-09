from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from api_admin.schema import REP_400, REP_403, REP_404, TAG_MATCHS, TAG_SCORES


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
