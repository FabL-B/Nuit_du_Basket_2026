from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.models import Edition
from matchs.models import Match
from api_public.serializers.planning import PlanningPublicSerializer
from api_public.openapi.planning import schema_planning_public


@schema_planning_public
class PlanningViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlanningPublicSerializer
    authentication_classes = []
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
        .filter(creneau__isnull=False, terrain__isnull=False)
        .order_by("creneau__debut", "terrain__ordre", "id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = self.request.query_params.get("tournoi") or self.request.query_params.get("tournoi_code")
        terrain = self.request.query_params.get("terrain")
        groupe = self.request.query_params.get("groupe")
        phase = self.request.query_params.get("phase")

        # Edition : par défaut, dernière édition
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
        if terrain:
            qs = qs.filter(terrain_id=terrain)
        if groupe:
            qs = qs.filter(groupe_id=groupe)
        if phase:
            qs = qs.filter(phase_globale__type_phase=phase)

        return qs
