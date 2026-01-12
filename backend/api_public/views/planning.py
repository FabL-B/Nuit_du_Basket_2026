from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from matchs.models import Match
from api_public.serializers.planning import PlanningPublicSerializer


class PlanningViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlanningPublicSerializer

    queryset = (
        Match.objects.all()
        .select_related(
            "creneau",
            "terrain",
            "phase_globale",
            "sous_phase",
            "sous_phase__tournoi",
            "groupe",
            "equipe_a",
            "equipe_b",
        )
        # public = uniquement ce qui est planifié
        .filter(creneau__isnull=False, terrain__isnull=False)
        .order_by("creneau__debut", "terrain__ordre", "id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        edition = self.request.query_params.get("edition")
        tournoi = self.request.query_params.get("tournoi")  # ex: ROOKIE
        terrain = self.request.query_params.get("terrain")
        groupe = self.request.query_params.get("groupe")

        if edition:
            qs = qs.filter(edition_id=edition)
        if tournoi:
            qs = qs.filter(sous_phase__tournoi__code=tournoi)
        if terrain:
            qs = qs.filter(terrain_id=terrain)
        if groupe:
            qs = qs.filter(groupe_id=groupe)

        return qs
