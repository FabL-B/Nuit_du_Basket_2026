from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from inscriptions.models import Equipe
from api_public.serializers.equipes import (
    EquipePublicListSerializer,
    EquipePublicDetailSerializer,
)


class EquipeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    queryset = (
        Equipe.objects.select_related("edition", "tournoi")
        .prefetch_related(
            "joueurs",
            "groupes",
            "groupes__groupe",
            "groupes__groupe__sous_phase",
            "groupes__groupe__sous_phase__phase_globale",
        )
        .order_by("id")
    )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EquipePublicDetailSerializer
        return EquipePublicListSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        categorie = self.request.query_params.get("categorie")
        tournoi = self.request.query_params.get("tournoi") or self.request.query_params.get(
            "tournoi_code"
        )
        groupe = self.request.query_params.get("groupe")

        # alias categorie -> tournoi_code
        tournoi_code = categorie or tournoi

        # Edition par défaut : dernière
        if edition:
            qs = qs.filter(edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if last:
                qs = qs.filter(edition=last)
            else:
                return qs.none()

        if tournoi_code:
            qs = qs.filter(tournoi__code=tournoi_code)

        if groupe:
            qs = qs.filter(groupes__groupe_id=groupe).distinct()

        # Public: en général on veut éviter BROUILLON
        qs = qs.exclude(statut="BROUILLON")

        return qs
