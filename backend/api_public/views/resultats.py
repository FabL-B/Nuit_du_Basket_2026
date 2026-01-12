from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from matchs.models import Match
from api_public.serializers.planning import PlanningPublicSerializer


class ResultatsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlanningPublicSerializer

    queryset = (
        Match.objects
        .select_related(
            "creneau",
            "terrain",
            "phase_globale",
            "sous_phase",
            "sous_phase__tournoi",
            "groupe",
            "equipe_a",
            "equipe_b",
            "score",
        )
        .filter(score__isnull=False)
        .order_by("creneau__debut", "terrain__ordre", "id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = self.request.query_params.get("tournoi") or self.request.query_params.get("tournoi_code")
        phase = self.request.query_params.get("phase")
        groupe = self.request.query_params.get("groupe")

        # Edition par défaut : dernière
        if edition:
            qs = qs.filter(edition_id=edition)
        else:
            last_edition = Edition.objects.order_by("-date_evenement").first()
            if last_edition:
                qs = qs.filter(edition=last_edition)
            else:
                return qs.none()

        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if phase:
            qs = qs.filter(phase_globale__type_phase=phase)
        if groupe:
            qs = qs.filter(groupe_id=groupe)

        return qs
