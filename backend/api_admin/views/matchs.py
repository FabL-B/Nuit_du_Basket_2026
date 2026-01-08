from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser

from matchs.models import Match
from matchs.models import MatchSheet
from api_admin.serializers.matchs import MatchSerializer
from api_admin.serializers.feuilles import MatchSheetSerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = MatchSerializer

    queryset = (
        Match.objects.all()
        .select_related(
            "edition",
            "phase_globale",
            "sous_phase",
            "sous_phase__tournoi",
            "groupe",
            "equipe_a",
            "equipe_b",
            "creneau",
            "terrain",
        )
        .order_by("id")
    )

    def get_queryset(self):
        qs = super().get_queryset()

        # filtres
        edition_id = self.request.query_params.get("edition")
        phase_globale_id = self.request.query_params.get("phase_globale")
        sous_phase_id = self.request.query_params.get("sous_phase")
        tournoi_code = self.request.query_params.get("tournoi_code")
        groupe_id = self.request.query_params.get("groupe")
        terrain_id = self.request.query_params.get("terrain")
        creneau_id = self.request.query_params.get("creneau")
        statut = self.request.query_params.get("statut")

        if edition_id:
            qs = qs.filter(edition_id=edition_id)
        if phase_globale_id:
            qs = qs.filter(phase_globale_id=phase_globale_id)
        if sous_phase_id:
            qs = qs.filter(sous_phase_id=sous_phase_id)
        if tournoi_code:
            qs = qs.filter(sous_phase__tournoi__code=tournoi_code)
        if groupe_id:
            qs = qs.filter(groupe_id=groupe_id)
        if terrain_id:
            qs = qs.filter(terrain_id=terrain_id)
        if creneau_id:
            qs = qs.filter(creneau_id=creneau_id)
        if statut:
            qs = qs.filter(statut=statut)

        return qs

    @action(detail=True, methods=["post"], url_path="feuille")
    def generer_feuille(self, request, pk=None):
        match = self.get_object()

        feuille, created = MatchSheet.objects.get_or_create(match=match)

        serializer = MatchSheetSerializer(feuille)
        return Response(
            {
                "created": created,
                "feuille": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
