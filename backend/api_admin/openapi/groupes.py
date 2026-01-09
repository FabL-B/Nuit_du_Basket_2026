from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from api_admin.schema import REP_400, REP_403, REP_404, TAG_GROUPES


schema_groupes_viewset = extend_schema_view(
    list=extend_schema(
        tags=[TAG_GROUPES],
        summary="Lister les groupes",
        description=(
            "Retourne la liste des groupes.\n\n"
            "Usage typique : filtrer par sous_phase pour afficher uniquement les groupes d'une sous-phase."
        ),
        responses={200: None, 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_GROUPES],
        summary="Lire un groupe",
        description="Retourne le détail d'un groupe.",
        responses={200: None, 403: REP_403, 404: REP_404},
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
