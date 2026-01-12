from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from groupes.models import Groupe
from api_public.serializers.groupes import (
    GroupePublicSerializer,
    GroupeDetailPublicSerializer,
)


class GroupeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    queryset = (
        Groupe.objects
        .select_related(
            "sous_phase",
            "sous_phase__phase_globale",
            "sous_phase__tournoi",
            "sous_phase__tournoi__edition",
        )
        .prefetch_related("equipes", "equipes__equipe")
        .order_by("sous_phase__tournoi__code", "sous_phase__branche", "code", "id")
    )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GroupeDetailPublicSerializer
        return GroupePublicSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = self.request.query_params.get("tournoi") or self.request.query_params.get("tournoi_code")
        phase = self.request.query_params.get("phase")
        branche = self.request.query_params.get("branche")

        # Edition par défaut : dernière
        if edition:
            qs = qs.filter(sous_phase__tournoi__edition_id=edition)
        else:
            last = Edition.objects.order_by("-date_evenement").first()
            if last:
                qs = qs.filter(sous_phase__tournoi__edition=last)
            else:
                return qs.none()

        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if phase:
            qs = qs.filter(sous_phase__phase_globale__type_phase=phase)
        if branche:
            qs = qs.filter(sous_phase__branche=branche)

        return qs
