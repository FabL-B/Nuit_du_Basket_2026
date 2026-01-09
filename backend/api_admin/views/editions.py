from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import Edition
from api_admin.serializers.editions import EditionSerializer
from api_admin.schema import TAG_EDITIONS, REP_400, REP_403, REP_404


@extend_schema_view(
    list=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Lister les éditions",
        description=(
            "Retourne la liste des éditions (une édition = une année/évènement Nuit du Basket).\n\n"
            "Une édition contient la date, l'heure de début, et la durée d'un créneau."
        ),
        responses={200: None, 403: REP_403},
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
        responses={201: None, 400: REP_400, 403: REP_403},
    ),
    retrieve=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Lire une édition",
        description="Retourne le détail d'une édition.",
        responses={200: None, 403: REP_403, 404: REP_404},
    ),
    update=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Modifier une édition",
        description=(
            "Modifie une édition.\n\n"
            "Attention: plus tard on bloquera certaines modifications quand le tournoi a démarré "
            "(règle process, pas implémentée ici)."
        ),
        responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    partial_update=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Modifier partiellement une édition",
        description="PATCH sur une édition.",
        responses={200: None, 400: REP_400, 403: REP_403, 404: REP_404},
    ),
    destroy=extend_schema(
        tags=[TAG_EDITIONS],
        summary="Supprimer une édition",
        description=(
            "Supprime une édition.\n\n"
            "Note: si tu veux interdire la suppression après inscriptions/matchs, "
            "ça se fera plus tard (règle process)."
        ),
        responses={204: None, 403: REP_403, 404: REP_404},
    ),
)
class EditionViewSet(viewsets.ModelViewSet):
    queryset = Edition.objects.all().order_by("-date_evenement")
    serializer_class = EditionSerializer
