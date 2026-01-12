from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from api_admin.schema import REP_400, REP_403, REP_404, TAG_EDITIONS
from api_admin.serializers.editions import EditionSerializer
from api_admin.serializers.planning_global import PlanningGlobalInputSerializer


schema_generer_planning_global = extend_schema(
    tags=[TAG_EDITIONS],
    summary="Générer le planning global d’une édition",
    description=(
        "Génère le planning global pour l’édition en planifiant les matchs "
        "de plusieurs phases (phase 1 obligatoire, phase 2 et phase finale optionnelles).\n\n"
        "Contraintes:\n"
        "- Les phases référencées doivent appartenir à la même édition.\n"
        "- Le body est validé via `PlanningGlobalInputSerializer`."
    ),
    request=PlanningGlobalInputSerializer,
    responses={
        200: OpenApiResponse(
            description="Planning global généré.",
            examples=[
                OpenApiExample(
                    "Réponse planning-global/generer",
                    value={
                        "detail": "Planning global généré.",
                        "edition_id": 3,
                        "resume": {
                            "creneaux_crees": 12,
                            "matchs_planifies": 96,
                            "detail": "Résumé sérialisé (dataclass/namespace).",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erreur métier ou phases invalides.",
            examples=[
                OpenApiExample(
                    "Phases introuvables",
                    value={"detail": "Phase(s) introuvable(s) pour cette édition."},
                    response_only=True,
                    status_codes=["400"],
                ),
                OpenApiExample(
                    "Erreur planning global",
                    value={"detail": "Impossible de générer le planning global (contrainte...)."},
                    response_only=True,
                    status_codes=["400"],
                ),
            ],
        ),
        403: REP_403,
        404: REP_404,
    },
    examples=[
        OpenApiExample(
            "Body planning-global/generer",
            value={
                "phase1_id": 12,
                "phase2_id": 34,
                "phase_finale_id": 56,
                "heure_debut_concours": "18:00:00",
                "duree_concours_minutes": 120,
            },
            request_only=True,
        )
    ],
)


schema_editions_viewset = extend_schema_view(
    list=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Lister les éditions",
        description=(
            "Retourne la liste des éditions (une édition = une année/évènement Nuit du Basket).\n\n"
            "Une édition contient la date, l'heure de début, et la durée d'un créneau."
        ),
        responses={200: EditionSerializer(many=True), 403: REP_403},
    ),
    create=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Créer une édition",
        description=(
            "Crée une nouvelle édition.\n\n"
            "Règles:\n"
            "- nom unique\n"
            "- date_evenement unique\n"
            "- heure_debut a un défaut (14:00) mais peut être modifiée"
        ),
        responses={201: EditionSerializer, 400: REP_400, 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Lire une édition",
        description="Retourne le détail d'une édition.",
        responses={200: EditionSerializer, 403: REP_403, 404: REP_404},
    ),
    update=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Modifier une édition",
        description=(
            "Modifie une édition.\n\n"
            "Attention: plus tard on bloquera certaines modifications quand le tournoi a démarré "
            "(règle process, pas implémentée ici)."
        ),
        responses={200: EditionSerializer, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    partial_update=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Modifier partiellement une édition",
        description="PATCH sur une édition.",
        responses={200: EditionSerializer, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    destroy=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Supprimer une édition",
        description=(
            "Supprime une édition.\n\n"
            "Note: si tu veux interdire la suppression après inscriptions/matchs, "
            "ça se fera plus tard (règle process)."
        ),
        responses={204: OpenApiResponse(description="Supprimé."), 403: REP_403, 404: REP_404},
    ),
)
