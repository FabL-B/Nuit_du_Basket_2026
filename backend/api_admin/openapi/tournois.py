from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from api_admin.schema import REP_400, REP_403, REP_404, TAG_TOURNOIS
from api_admin.serializers.tournois import TournoiSerializer


schema_tournois_viewset = extend_schema_view(
    list=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Lister les tournois",
        description=(
            "Retourne les tournois d'une édition.\n\n"
            "Règle : il y a toujours 3 tournois par édition (Rookie / Loisir / Compétiteur).\n"
            "Les codes sont figés ; on n'ajoute pas de nouveaux types de tournois."
        ),
        responses={200: TournoiSerializer(many=True), 403: REP_403},
    ),
    create=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Créer un tournoi",
        description=(
            "Crée un tournoi pour une édition.\n\n"
            "Attention : dans le modèle métier, on s’attend généralement à 3 tournois fixes par édition "
            "(selon ta règle)."
        ),
        responses={201: TournoiSerializer, 400: REP_400, 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Lire un tournoi",
        description="Retourne le détail d'un tournoi.",
        responses={200: TournoiSerializer, 403: REP_403, 404: REP_404},
    ),
    update=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Modifier un tournoi",
        description=(
            "Modifie les informations éditables d'un tournoi.\n\n"
            "Attention : le champ `code` est figé (ROOKIE/LOISIR/COMPETITEUR)."
        ),
        responses={200: TournoiSerializer, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    partial_update=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Modifier partiellement un tournoi",
        description="PATCH sur un tournoi (libellé principalement).",
        responses={200: TournoiSerializer, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    destroy=extend_schema(
        tags=[TAG_TOURNOIS],
        summary="Supprimer un tournoi",
        description="Supprime un tournoi.",
        responses={204: OpenApiResponse(description="Supprimé."), 403: REP_403, 404: REP_404},
    ),
)
