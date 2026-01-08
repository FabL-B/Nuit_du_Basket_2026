from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from phases.models import PhaseGlobale
from phases.services_cloture import cloturer_phase_globale, ErreurCloturePhase
from phases.services_phase2 import previsualiser_phase2_depuis_phase1, ErreurGenerationPhase2
from api_admin.serializers.phases import PhaseGlobaleSerializer


class PhaseGlobaleViewSet(viewsets.ModelViewSet):
    queryset = PhaseGlobale.objects.all().order_by("-id")
    serializer_class = PhaseGlobaleSerializer

    @action(detail=True, methods=["post"], url_path="cloturer")
    def cloturer(self, request, pk=None):
        phase = self.get_object()
        try:
            resume = cloturer_phase_globale(phase)
        except ErreurCloturePhase as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"phase_id": phase.id, "groupes": resume.groupes, "matchs_total": resume.matchs_total},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="phase2-preview")
    def phase2_preview(self, request, pk=None):
        phase1 = self.get_object()
        try:
            preview = previsualiser_phase2_depuis_phase1(phase1)
        except ErreurGenerationPhase2 as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "phase2_id": preview.phase2_id,
                "tournois_impairs": preview.tournois_impairs,
                "propositions": [
                    {
                        "code_tournoi": p.code_tournoi,
                        "nb_total": p.nb_total,
                        "nb_challenge_min": p.nb_challenge_min,
                        "nb_challenge_max": p.nb_challenge_max,
                        "equipe_ids_ordre": p.equipe_ids_ordre,
                    }
                    for p in preview.propositions
                ],
            },
            status=status.HTTP_200_OK,
        )
