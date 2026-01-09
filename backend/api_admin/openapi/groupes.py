from drf_spectacular.utils import extend_schema, OpenApiExample
from api_admin.schema import TAG_GROUPES, REP_400, REP_403, REP_404

swap_equipes_schema = extend_schema(
    tags=[TAG_GROUPES],
    summary="Interchanger deux équipes entre deux groupes",
    description=(
        "Interchange deux équipes entre deux groupes.\n\n"
        "Contraintes strictes :\n"
        "- mêmes sous-phase\n"
        "- cohérence édition/tournoi (validée)\n"
        "- opération atomique"
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
